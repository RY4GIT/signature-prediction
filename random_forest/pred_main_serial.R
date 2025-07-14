# Script to execute predictions with trained Random Forest models
# This code runs Random Forest in a serial (non-parallel) computing mode

# __________________________________________
# Package imports (optional)
#
# # Set CRAN mirror
# options(repos = c(CRAN = "https://cran.rstudio.com/"))
#
# # Function to install packages if not already installed
# install_if_missing <- function(packages) {
#   new_packages <- packages[!(packages %in% installed.packages()[, "Package"])]
#   if (length(new_packages)) install.packages(new_packages, dependencies = TRUE)
# }
#
# # List of all required packages
# packages <- c(
#   "tidyverse", "randomForest", "caret",
#   "doParallel", "dplyr", "foreach", "yaml"
# )
#
# # Install missing packages
# install_if_missing(packages)

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

# Load configuration. Choose from (1) or (2) and
# comment out the ones that you didn't select.
Sys.setenv(R_CONFIG_ACTIVE = "default")

# Start the timer
start_time <- proc.time()

# ___________________________________________________________________________
# (1) Load configuration from a file path
# Set the configuration file path directly
# config_file <- "./random_forest/configs/win/config_test_pred.yml"

# # Check if the file exists to avoid runtime errors
# if (!file.exists(config_file)) {
#   stop("Configuration file not found: ", config_file)
# }

# ___________________________________________________________________________
# (2) Load configuration as an argument
args <- commandArgs(trailingOnly = TRUE)
config_file <- args[1]

# If you choose this, run the code using bash/shell
#
# How to run in Windows:
# > cd signature-prediction\random_forest
# > run.bat

# How to run in Linux:
# > cd signature-prediction\random_forest
# > .\run.sh

# ___________________________________________________________________________
config <- yaml::read_yaml(config_file)
print(config)


# ___________________________________________________________________________
# Load directory paths
home_dir <- config$paths$home_dir
# Output to the model directory
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
  filter(if_all(-gauge_id, ~ !is.na(.) & !is.infinite(.)))

rows_removed <- total_rows - nrow(attrs_pred)
print(paste(
  "Rows removed:",
  rows_removed,
  "(",
  round(rows_removed / total_rows * 100, 2),
  "%)"
))
print(paste("Rows remaining:", nrow(attrs_pred)))

#############################################
# EXECUTION
#############################################

# Define a function to predict signatures using the trained model
predict_signature <- function(model_path, new_data) {
  print(paste("Predicting signature from model:", model_path))

  # Load the model
  model <- readRDS(model_path)

  # Ensure new_data has the same structure as training data
  required_predictors <- setdiff(names(model$trainingData), ".outcome")
  missing_cols <- setdiff(required_predictors, names(new_data))

  if (length(missing_cols) > 0) {
    stop(
      "Missing required predictor columns: ",
      paste(missing_cols, collapse = ", ")
    )
  }

  # Make predictions
  predictions <- predict(model, newdata = new_data)
  return(predictions)
}

print(paste("Predicting signatures from models in:", out_path))
# Loop through signatures (1 RF model per signature)
out_sig_predictions <- list()
for (sig in config$sigs_predict) {
  # Execute the prediction
  model_path <- file.path(out_path, paste0("model_", sig, ".rds"))
  predicted_sig <- predict_signature(model_path, attrs_pred)

  # Append predicted signature values
  out_sig_predictions[[sig]] <- data.frame(
    gauge_id = attrs_pred$gauge_id,
    prediction = predicted_sig,
    sig_name = sig
  )
}


#############################################
# FINALIZE
#############################################

print(paste("Finalizing predictions. Outputting results to:", out_path))

# Output the results
all_sig_predictions <- bind_rows(out_sig_predictions)
output_filename <- paste0(
  "predicted_signatures_",
  config$experiment_name,
  ".csv"
)
write.csv(
  all_sig_predictions,
  file.path(out_path, output_filename),
  row.names = FALSE
)

# Output the config file
out_config_filename <- paste0("config_pred_", config$experiment_name, ".yaml")
yaml::write_yaml(config, file.path(out_path, out_config_filename))

# Stop the timer
end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time: ", round(execution_time[3], 0), "seconds"))
