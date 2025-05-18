# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

# How to run in Windows: 
# > cd signature-prediction\random_forest
# > run.bat

# UNCOMMENT THIS IF YOUR COMPUTER DOES NOT HAVE THE REQUIRED PACKAGES
# # Set CRAN mirror
# options(repos = c(CRAN = "https://cran.rstudio.com/"))

# # Function to install packages if not already installed
# install_if_missing <- function(packages) {
#   new_packages <- packages[!(packages %in% installed.packages()[, "Package"])]
#   if (length(new_packages)) install.packages(new_packages, dependencies = TRUE)
# }

# # List of all required packages
# packages <- c(
#   "tidyverse", "randomForest", "caret", 
#   "doParallel", "dplyr", "foreach", "yaml", "iml"
# )

# # Install missing packages
# install_if_missing(packages)

library(tidyverse)
library(randomForest)
library(caret)
library(doParallel)
library(dplyr)
library(foreach)
library(iml)
library(data.table)

#############################################
# INITIALIZATION
#############################################

# _______________________________________________________________________________________________________________
# Load configuration
Sys.setenv(R_CONFIG_ACTIVE = "default")
args <- commandArgs(trailingOnly = TRUE)
config_file <- args[1]
config <- yaml::read_yaml(config_file)
print(config)

# ____________________________________________________________
# Load directory paths
home_dir <- config$paths$home_dir

# Create output directory
username <- Sys.info()[["user"]] # Get current username
formatted_datetime <- format(Sys.time(), "%Y%m%d")
out_path <- file.path(home_dir, config$paths$out_dir, paste0("output_", username, "_", formatted_datetime, "_", config$experiment_name))
if (!dir.exists(out_path)) {
  dir.create(out_path, recursive = TRUE)
  message("Directory created: ", out_path)
} else {
  message("Directory already exists.")
}
print(config$experiment_name)

# Start the timer
start_time <- proc.time()

# _______________________________________________________________________________________________________________
# Load datasets
# Here, "training set" is defined as a dataset used to fit the parameters
# "testing set" is defined as a dataset used to provide an evaluation of a model fit

# Define a function to load and process the signature data
load_signatures <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)

  # Select the gauge_id and all the specified columns from the data
  # and return it as a data frame
  data %>%
    select(gauge_id, all_of(config$sigs_predict)) %>%
    as.data.frame() # Ensure the output is a data frame
}

print("Loading signatures")
sigs_train_path <- file.path(home_dir, config$paths$train$signatures)
sigs_train <- load_signatures(sigs_train_path)

print("Loading attributes")
# Define a function to load and process the attributes data
load_attrs <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)

  # Select the gauge_id and the attributes of interest
  # and return it as a data frame
  data %>%
    select(gauge_id, all_of(config$attrs_of_interest), cluster) %>%
    as.data.frame()
}

print("Loading training attributes")
attrs_train_path <- file.path(home_dir, config$paths$train$attributes)
attrs_train <- load_attrs(attrs_train_path)

print("Loading test attributes")
attrs_test_path <- file.path(home_dir, config$paths$test$attributes)
attrs_test <- load_attrs(attrs_test_path)

# _______________________________________________________________________________________________________________
# If running the model by cluster, filter and get the subset of the data
print("Filtering by cluster")
if (config$filter_by_cluster$run) {
  attrs_train <- attrs_train %>%
    filter(cluster == config$filter_by_cluster$name) %>%
    select(-cluster)
  attrs_test <- attrs_test %>%
    filter(cluster == config$filter_by_cluster$name) %>%
    select(-cluster)
  message("Selected ", nrow(attrs_train), " gauges in: ", config$filter_by_cluster$name)
} else {
  attrs_train <- attrs_train %>%
    select(-cluster)
}

#############################################
# EXECUTION
#############################################

# _______________________________________________________________________________________________________________
# Parallel pool setup
print("initiating parallel pool")

# Set up parallel backend for caret
num_cores <- min(4, detectCores())
cl <- makeCluster(num_cores)
registerDoParallel(cl)
print(paste("Using", num_cores, "cores for parallel processing"))

# _______________________________________________________________________________________________________________
# Random forest initialization

set.seed(config$settings$seed)

# Define repeated cross-validation with 10 folds and three repeats
# allow for parameter tuning, for mtry grid; range through the total number of predictor variables
hyper_grid <- expand.grid(
  mtry = c(1:(length(attrs_train) - 1))
)

# Set up properly structured seeds for reproducibility
num_folds <- config$settings$num_folds

# Create a vector of seeds for each iteration (for parallel reproducibility)
# For regular CV: we need folds + 1
seeds <- vector(mode = "list", length = num_folds + 1)

# For each fold, we need a vector with length = number of tuning parameter combinations
for (i in 1:num_folds) {
  seeds[[i]] <- sample.int(1000, nrow(hyper_grid))
}

# For the final model, we need a single integer
seeds[[num_folds + 1]] <- sample.int(1000, 1)

# Set up the training control with CV and the proper seeds
kfold_cv <- trainControl(
  method = "cv",
  number = num_folds,
  search = "grid",
  verboseIter = TRUE,
  seeds = seeds,
  allowParallel = TRUE  # Enable parallel within caret
)

# Prepare output list
out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()
out_shap_values <- list()

print("Start training multiple Random Forest models")
# Process each signature
results <- list()
for (sig in config$sigs_predict) {
  tryCatch({
    message(paste("Processing signature:", sig))
    
    # _______________________________________________________________________________________________________________
    # TRAINING

    # define repeated cross-validation with 10 folds and three repeats
    # allow for parameter tuning, for mtry grid; range through the total number of predictor variables

    train_data <- attrs_train %>%
      inner_join(sigs_train %>% select(gauge_id, all_of(sig)), by = "gauge_id") %>%
      select(-gauge_id) %>%
      drop_na() %>%
      filter_all(all_vars(!is.infinite(.)))
    
    # Ensure we're using a numeric target for regression
    train_data[[sig]] <- as.numeric(train_data[[sig]])
    
    # Try to train with error handling
    forest_result <- tryCatch({
      # Training the model with caret's parallel capabilities
      forest <- train(
        # signature to predict
        formula(paste(sig, "~ .")),
        # input attribute dataset, includes signature
        data = train_data,
        # Random forest method
        method = "rf",
        # metric to evaluate model performance
        metric = config$settings$eval_metric,
        # Number of trees
        ntree = config$settings$ntree,
        # adding the repeated cross validation
        trControl = kfold_cv,
        # hyperparameter testing
        tuneGrid = hyper_grid,
        # return importance, want %IncMSE data
        importance = TRUE
      )
      forest  # Return the forest object if successful
    }, error = function(e) {
      message(paste("Error training model for signature", sig, ":", e$message))
      NULL  # Return NULL if there was an error
    })
    
    # Check if model training was successful
    if (is.null(forest_result)) {
      # Return placeholder values if training failed
      results[[sig]] <- list(
        sig_predictions = data.frame(gauge_id = attrs_test$gauge_id, prediction = NA, sig_name = sig),
        r2 = data.frame(sig_name = sig, r_squared = NA),
        var_importance = data.frame(predictor = names(train_data)[names(train_data) != sig], 
                                  Importance = NA, 
                                  sig_name = sig),
        shap_values = data.frame(feature = names(train_data)[names(train_data) != sig],
                               phi = NA,
                               phi.var = NA,
                               feature_value = NA,
                               sig_name = sig)
      )
      next  # Skip to the next signature
    }
    
    # Use the result if successful
    forest <- forest_result  
    print(forest)
    print(forest$finalModel)

    # _______________________________________________________________________________________________________________
    # Predict signature values
    test_data <- attrs_test %>%
      drop_na() 
    
    predictions <- predict(forest, test_data %>% select(-gauge_id))
    
    # _______________________________________________________________________________________________________________
    # Append results
    
    # append r2 value
    if (is.null(forest$finalModel$rsq) || length(forest$finalModel$rsq) == 0) {
      out_r2 <- data.frame(sig_name = sig, r_squared = NA)  # Use NA when no r_squared value is calculated
    } else {
      out_r2 <- data.frame(sig_name = sig, r_squared = tail(forest$finalModel$rsq, 1))
    }
    
    # append variable importance
    var_imp_result <- tryCatch({
      importance_data <- importance(forest$finalModel, type = 1, scale = TRUE)
      if (is.null(importance_data) || nrow(importance_data) == 0) {
        data.frame(predictor = names(train_data)[names(train_data) != sig], 
                  Importance = NA, 
                  sig_name = sig)
      } else {
        importance_data %>%
          as.data.frame() %>%
          tibble::rownames_to_column(var = "predictor") %>%
          dplyr::mutate(sig_name = sig)
      }
    }, error = function(e) {
      message(paste("Error getting variable importance for", sig, ":", e$message))
      data.frame(predictor = names(train_data)[names(train_data) != sig], 
                Importance = NA, 
                sig_name = sig)
    })
    
    out_var_importance <- var_imp_result
    
    # append predicted signature values 
    out_sig_predictions <- data.frame(gauge_id = test_data$gauge_id, prediction = predictions, sig_name = sig)
    
    # _______________________________________________________________________________________________________________
    # Calculate SHAP values
    
    # Try to calculate SHAP values with error handling
    shap_result <- tryCatch({
      # Create a predictor object for the model
      predictor <- Predictor$new(forest$finalModel, data = train_data %>% select(-all_of(sig)), y = train_data[[sig]])
      
      # Calculate SHAP values
      shap <- Shapley$new(predictor, x.interest = train_data %>% select(-all_of(sig)))
      shap_values <- shap$results
      
      # Format SHAP values
      shap_values %>%
        as.data.frame() %>%
        dplyr::mutate(
          feature = gsub("=.*", "", feature),
          feature_value = as.numeric(gsub(".*=", "", feature.value)),
          sig_name = sig
        ) %>%
        select(feature, phi, phi.var, feature_value, sig_name)
    }, error = function(e) {
      message(paste("Error calculating SHAP values for", sig, ":", e$message))
      data.frame(
        feature = names(train_data)[names(train_data) != sig],
        phi = NA,
        phi.var = NA,
        feature_value = NA,
        sig_name = sig
      )
    })
    
    out_shap_values <- shap_result

    # Save the trained model for this signature
    if (!config$filter_by_cluster$run) {
      model_file_name <- file.path(out_path, paste0("model_", sig, ".rds"))
      saveRDS(forest, model_file_name)
      message(paste("Saved model for", sig, "to", model_file_name))
    }

    # Store results for this signature
    results[[sig]] <- list(
      sig_predictions = out_sig_predictions, 
      r2 = out_r2,
      var_importance = out_var_importance,
      shap_values = out_shap_values
    )

  }, error = function(e) {
    message(paste("Global error for signature", sig, ":", e$message))
    # Return placeholders if an error occurs
    results[[sig]] <- list(
      sig_predictions = data.frame(gauge_id = attrs_test$gauge_id, prediction = NA, sig_name = sig),
      r2 = data.frame(sig_name = sig, r_squared = NA),
      var_importance = data.frame(predictor = names(attrs_train)[names(attrs_train) != "gauge_id"], 
                                Importance = NA, 
                                sig_name = sig),
      shap_values = data.frame(feature = names(attrs_train)[names(attrs_train) != "gauge_id"],
                             phi = NA,
                             phi.var = NA,
                             feature_value = NA,
                             sig_name = sig)
    )
  })
}

#############################################
# FINALIZE
#############################################

# Stop parallel cluster
stopCluster(cl)

print("Finished the training and unlisting results")
# Extract results from the list
out_sig_predictions <- lapply(results, `[[`, "sig_predictions")
out_r2 <- lapply(results, `[[`, "r2")
out_var_importance <- lapply(results, `[[`, "var_importance")
out_shap_values <- lapply(results, `[[`, "shap_values")

# Combine all the elements in the lists (results from multiple signatures) into data frames
all_sig_predictions <- bind_rows(out_sig_predictions)
all_r2 <- bind_rows(out_r2)
all_var_importance <- bind_rows(out_var_importance)
all_shap_values <- bind_rows(out_shap_values)


# Save output to CSV
print("Saving output to CSV")
write.csv(all_sig_predictions, file.path(out_path, "predicted_signatures_train.csv"), row.names = FALSE)
write.csv(all_var_importance, file.path(out_path, "var_importance.csv"), row.names = FALSE)
write.csv(all_r2, file.path(out_path, "r_squared.csv"), row.names = FALSE)
write.csv(all_shap_values, file.path(out_path, "shap_values.csv"), row.names = FALSE)

print("Saving config file")
# Save config file
yaml::write_yaml(config, file.path(out_path, "config_train.yaml"))

# ______________________________________________________
# Calculate execution time
end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time: ", execution_time[3], "seconds"))
print(paste("Output results to", out_path))
