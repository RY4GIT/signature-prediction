# script to execute random forest models, predicting hydrologic signatures based on catchment attribute datasets
# # Note that originally was generating random forests in Python, but decided to use R packages used in other studies

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
library(yaml)

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
formatted_datetime <- format(Sys.time(), "%Y%m%d")
out_path <- file.path(home_dir, config$paths$out_dir, paste0("output_", formatted_datetime, "_", config$experiment_name))
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
# Load data

# Define a function to load and process the signature data
load_signatures <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)
  
  # Select the gauge_id and all the specified columns from the data
  # and return it as a data frame
  data %>%
    select(gauge_id, all_of(config$sigs_predict)) %>%
    as.data.frame()
}

sigs_train_path <- file.path(home_dir, config$paths$train$signatures)
sigs_train <- load_signatures(sigs_train_path)


# Attributes
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

if (config$filter_by_ecoregion$run) {
  attrs_train <- attrs_train %>%
    filter(ecoregion == config$filter_by_ecoregion$name) %>%
    select(-ecoregion)
  attrs_test <- attrs_test %>%
    filter(ecoregion == config$filter_by_ecoregion$name) %>%
    select(-ecoregion)
  message("Selected ", nrow(attrs_train), " gauges in: ", config$filter_by_ecoregion$name)
}

#############################################
# EXECUTION
#############################################

# _______________________________________________________________________________________________________________
# Random forest initialization

set.seed(config$settings$seed)

# define repeated cross-validation with 10 folds and three repeats
# allow for parameter tuning, for mtry grid; range through the total number of predictor variables
hyper_grid <- expand.grid(mtry = 1:(ncol(attrs_train)-1))
kfold_cv <- trainControl(method = "cv", number = config$settings$num_folds, search = "grid", verboseIter = TRUE)

out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()

for(sig in config$sigs_predict){
  
  print(paste0("Processing:", sig))
  
  # _______________________________________________________________________________________________________________
  # TRAINING
  train_data <- attrs_train %>%
    left_join(sigs_train %>% select(gauge_id, all_of(sig)), by = "gauge_id") %>%
    select(-gauge_id) %>%
    drop_na() 

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
    # hyper parameter testing
    tuneGrid = hyper_grid,
    # return importance, want %IncMSE data
    importance = TRUE
  )
  
  print(forest)
  print(forest$finalModel)
  
  # _______________________________________________________________________________________________________________
  # Save the model to a file
  
  # append r2 value
  if(length(forest$finalModel$rsq) == 0) {
      out_r2[[sig]] <- NA  # Use NA when no r_squared value is calculated
    } else {
      out_r2[[sig]] <- mean(forest$final$rsq)
    }
  
  # Append to larger output list, variable importance
  if(nrow(importance(forest$finalModel, type = 1, scale = TRUE)) == 0) {
    out_var_importance[[sig]] <- data.frame(predictor = NA, Importance = NA, sig_name = sig)
  } else {
    out_var_importance[[sig]] <- importance(forest$finalModel, type = 1, scale = TRUE) %>%
      as.data.frame() %>%
      tibble::rownames_to_column(var = "predictor") %>%
      dplyr::mutate(sig_name = sig)
  }
  
  
  # _______________________________________________________________________________________________________________
  # Predict signature value / can be on a test dataset. Currently it is used to simply get predicted signature values from training & validation
  test_data <- attrs_test %>%
    drop_na() 
  
  predictions <- predict(forest, test_data%>%select(-gauge_id))
  
  # Store predictions in the list
  if(length(predictions) == 0) {
    out_sig_predictions[[sig]] <- data.frame(gauge_id = NA, prediction = NA, sig_name = sig)
  } else {
    out_sig_predictions[[sig]] <- data.frame(gauge_id = test_data$gauge_id, prediction = predictions, sig_name = sig)
  }
}

# _______________________________________________________________________________________________________________
#############################################
# FINALIZE
#############################################

# Output the results
all_sig_predictions <- bind_rows(out_sig_predictions)
all_var_importance <- bind_rows(out_var_importance)
all_r2 <- bind_rows(out_r2) %>%
  pivot_longer(everything(), names_to = "sig_name", values_to = "r_squared")

write.csv(all_sig_predictions, file.path(out_path, "predicted_signatures.csv"), row.names = FALSE)
write.csv(all_var_importance, file.path(out_path, "var_importance.csv"), row.names = FALSE)
write.csv(all_r2, file.path(out_path, "r_squared.csv"), row.names = FALSE)

yaml::write_yaml(config, file.path(out_path, "config.yaml"))

end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time: ", execution_time[3], "seconds"))