# Script to execute predictions with trained Random Forest models
# This code runs Random Forest in a parallel computing mode

# __________________________________________
# Package imports
library(tidyverse)
library(randomForest)
library(caret)
library(dplyr)
library(doParallel)
library(foreach)
library(yaml)
library(iml)

#############################################
# INITIALIZATION
#############################################

# Load configuration
Sys.setenv(R_CONFIG_ACTIVE = "default")

# Start the timer
start_time <- proc.time()

# ___________________________________________________________________________
# (1) Load configuration from a file path
# Set the configuration file path directly
config_file <- "./random_forest/configs/win/config_test_pred.yml"

# Check if the file exists to avoid runtime errors
if (!file.exists(config_file)) {
  stop("Configuration file not found: ", config_file)
}

# ___________________________________________________________________________
# Load configuration
config <- yaml::read_yaml(config_file)
print(config)

# ___________________________________________________________________________
# Load directory paths
home_dir <- config$paths$home_dir
out_path <- file.path(home_dir, config$paths$predict$model_dir)
# Check if the output path exists
if (!dir.exists(out_path)) {
  stop("Model directory not found. Please check your configuration.")
}

# ___________________________________________________________________________
# Load attributes for prediction

# Define a function to load and process the attributes data
load_attrs <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)

  # Select the gauge_id and the attributes of interest
  # and return it as a data frame
  data %>%
    select(gauge_id, all_of(config$attrs_of_interest)) %>%
    as.data.frame()
}

# Load the attributes
attrs_pred_path <- file.path(home_dir, config$paths$predict$attributes)
attrs_pred_ <- load_attrs(attrs_pred_path)

# Filter out gauges with NaN or Inf attribute values
total_rows <- nrow(attrs_pred_)
print(paste("Total rows before filtering:", total_rows))

attrs_pred <- attrs_pred_ %>%
  filter(if_all(-gauge_id, ~!is.na(.) & !is.infinite(.)))

rows_removed <- total_rows - nrow(attrs_pred)
print(paste("Rows removed:", rows_removed, "(", round(rows_removed/total_rows*100, 2), "%)"))
print(paste("Rows remaining:", nrow(attrs_pred)))

#############################################
# SETUP PARALLELIZATION
#############################################

print("Initiating parallel pool")

# Register the parallel backend - use the smaller of 4 cores or what's available
# This avoids overloading shared systems
registerDoParallel(cores = min(4, detectCores()))

#############################################
# EXECUTION
#############################################

# Define a function to predict signatures using the trained model
predict_signature <- function(model_path, new_data) {
  # Load the model
  model <- readRDS(model_path)
  
  # Ensure new_data has the same structure as training data
  required_predictors <- setdiff(names(model$trainingData), ".outcome")
  missing_cols <- setdiff(required_predictors, names(new_data))
  
  if (length(missing_cols) > 0) {
    stop("Missing required predictor columns: ", paste(missing_cols, collapse=", "))
  }
  
  # Make predictions
  predictions <- predict(model, newdata = new_data)
  return(predictions)
}

# Execute predictions in parallel
print("Starting parallel predictions")
out_sig_predictions <- list()
results <- foreach(sig = config$sigs_predict, 
                   .packages = c("randomForest", "caret", "dplyr")) %dopar% {
  tryCatch({
    # Build the model path for this signature
    model_path <- file.path(out_path, paste0("model_", sig, ".rds"))
    
    # Check if model file exists
    if (!file.exists(model_path)) {
      warning(paste("Model file not found for signature", sig, ":", model_path))
    }
    
    # Execute the prediction for this signature
    predicted_values <- predict_signature(model_path, attrs_pred)
    
    # Return results as a list
    list(
      predictions = data.frame(
        gauge_id = attrs_pred$gauge_id, 
        prediction = predicted_values, 
        sig_name = sig
      )
    )
  }, error = function(e) {
    # Return NA values if an error occurs
    warning(paste("Error predicting signature", sig, ":", e$message))
  })
}

#############################################
# FINALIZE
#############################################

# Extract predictions from results
out_sig_predictions <- lapply(results, function(x) x$predictions)

# Combine all predictions into one data frame
all_sig_predictions <- bind_rows(out_sig_predictions)

# Generate output filename with experiment name
output_filename <- paste0("predicted_signatures_", config$experiment_name, "_mp.csv")
write.csv(all_sig_predictions, file.path(out_path, output_filename), row.names = FALSE)
print(paste("Predictions saved to:", output_filename))


# Output the config file
yaml::write_yaml(config, file.path(out_path, "config_pred.yaml"))

# Stop the timer
end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time:", round(execution_time[3], 0), "seconds"))

# Stop the parallel backend
stopImplicitCluster()