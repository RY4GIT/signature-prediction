# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

# How to run in Windows: 
# > cd signature-prediction\random_forest
# > run.bat

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

# # Before the loop, open a connection to a log file
# log_file <- file(file.path(out_path, "log.txt"), open = "wt")

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

sigs_train_path <- file.path(home_dir, config$paths$train$signatures)
sigs_train <- load_signatures(sigs_train_path)

# Define a function to load and process the attribute data
load_attrs <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)
  
  # Select the gauge_id and all the specified columns from the data
  # and return it as a data frame
  data %>%
    select(gauge_id, all_of(config$attrs_of_interest), ecoregion) %>%
    as.data.frame()
}

attrs_train_path <- file.path(home_dir, config$paths$train$attributes)
attrs_train <- load_attrs(attrs_train_path)

attrs_test_path <- file.path(home_dir, config$paths$test$attributes)
attrs_test <- load_attrs(attrs_test_path)

# _______________________________________________________________________________________________________________
# If running the model by ecoregion, filter and get the subset of the data
if (config$filter_by_ecoregion$run) {
  attrs_train <- attrs_train %>%
    filter(ecoregion == config$filter_by_ecoregion$name) %>%
    select(-ecoregion)
  attrs_test <- attrs_test %>%
    filter(ecoregion == config$filter_by_ecoregion$name) %>%
    select(-ecoregion)
  message("Selected ", nrow(attrs_train), " gauges in: ", config$filter_by_ecoregion$name)
} else {
  attrs_train <- attrs_train %>%
    select(-ecoregion)
}

#############################################
# EXECUTION
#############################################

# _______________________________________________________________________________________________________________
# Parallel pool
print("initiating parallel pool")
# Register the parallel backend
registerDoParallel(cores = config$parallel$nCores)


# _______________________________________________________________________________________________________________
# Random forest initialization

set.seed(config$settings$seed)

# Define repeated cross-validation with 10 folds and three repeats
# allow for parameter tuning, for mtry grid; range through the total number of predictor variables
hyper_grid <- expand.grid(
  mtry = c(1:(length(attrs_train)-1))
)

kfold_cv <- trainControl(method = "cv", number = config$settings$num_folds, search = "grid", verboseIter = TRUE)

# Prepare output list
out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()

print("Start multiple RFs")
# Multi-threadding --- each thread receives one RF model for one signature prediction 
results <- foreach(sig = config$sigs_predict, .packages = c("randomForest", "dplyr", "tidyr", "caret", "purrr")) %dopar% {
  # tryCatch({
  library(dplyr)  # Ensure dplyr is loaded
  library(tidyr)  # Ensure tidyr is loaded
  
  # # Prepare messages to log
  # log_messages <- character()
  # log_messages <- c(log_messages, paste("Processing:", sig, "\n"))
  
  # _______________________________________________________________________________________________________________
  # TRAINING

  # define repeated cross-validation with 10 folds and three repeats
  # allow for parameter tuning, for mtry grid; range through the total number of predictor variables

  train_data <- attrs_train %>%
    inner_join(sigs_train %>% select(gauge_id, all_of(sig)), by = "gauge_id") %>%
    select(-gauge_id) %>%
    drop_na() %>%
    filter_all(all_vars(!is.infinite(.)))
  
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

  print(forest)
  print(forest$finalModel)

  # _______________________________________________________________________________________________________________
  # Predict signature values
  test_data <- attrs_test %>%
    drop_na() 
  
  predictions <- predict(forest, test_data%>%select(-gauge_id))
# 
#   log_messages <- c(log_messages, "Completed processing for signature.")
#   
  
  # _______________________________________________________________________________________________________________
  # Append results
  
  # append r2 value
  if(length(forest$finalModel$rsq) == 0) {
    out_r2 <- data.frame(sig_name = sig, r_squared = NA)  # Use NA when no r_squared value is calculated
  } else {
    out_r2 <- data.frame(sig_name = sig, r_squared = mean(forest$final$rsq))
  }
  
  # append variable importance
  if(nrow(importance(forest$finalModel, type = 1, scale = TRUE)) == 0) {
    out_var_importance <- data.frame(predictor = NA, Importance = NA, sig_name = sig)
  } else {
    out_var_importance <- importance(forest$finalModel, type = 1, scale = TRUE) %>%
      as.data.frame() %>%
      tibble::rownames_to_column(var = "predictor") %>%
      dplyr::mutate(sig_name = sig)
  }
  
  # append predicted signature values 
  if(length(predictions) == 0) {
    out_sig_predictions <- data.frame(gauge_id = NA, prediction = NA, sig_name = sig)
  } else {
    out_sig_predictions <- data.frame(gauge_id = test_data$gauge_id, prediction = predictions, sig_name = sig)
  }
  
  # Summarize all output from one thread run in a list
  list(
    sig_predictions = out_sig_predictions, 
    r2 = out_r2,
    var_importance = out_var_importance
  )
  # }, error = function(e) {
  #   print(paste("An error occurred:", e$message))
  #   # Return NA values if an error occurs
  #   list(
  #     sig_predictions = data.frame(gauge_id = NA, prediction = NA, sig_name = sig),
  #     r2 = data.frame(sig_name = sig, r_squared = NA),
  #     var_importance = data.frame(predictor = NA, Importance = NA, sig_name = sig)
  #   )
}
  # )
# _______________________________________________________________________________________________________________
#############################################
# FINALIZE
#############################################

# Unlist results
out_sig_predictions <- lapply(results, `[[`, "sig_predictions")
out_r2 <- lapply(results, `[[`, "r2")
out_var_importance <- lapply(results, `[[`, "var_importance")

# Combine all the elements in the lists (results from multiple threads) into data frames
all_sig_predictions <- bind_rows(out_sig_predictions)
all_var_importance <- bind_rows(out_var_importance)
all_r2 <- bind_rows(out_r2)

# Save output to CSV
write.csv(all_sig_predictions, file.path(out_path, "predicted_signatures.csv"), row.names = FALSE)
write.csv(all_var_importance, file.path(out_path, "var_importance.csv"), row.names = FALSE)
write.csv(all_r2, file.path(out_path, "r_squared.csv"), row.names = FALSE)

# Save config file
yaml::write_yaml(config, file.path(out_path, "config.yaml"))

# # ______________________________________________________
# # After the loop, write all log messages to file
# # Log the execution time
# for (result in results) {
#   # Convert log messages to character if not already
#   if (!is.character(result$log_messages)) {
#     result$log_messages <- as.character(result$log_messages)
#   }
#   writeLines(result$log_messages, con = log_file)
# }

# ______________________________________________________
# Calculate execution time
end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time: ", execution_time[3], "seconds")) #, con = log_file)
print(paste("Output results to", out_path))
# close(log_file)

# Stop the parallel backend when done
stopImplicitCluster()
