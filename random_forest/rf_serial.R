# script to execute random forest models, predicting hydrologic signatures based on catchment attribute datasets
# Note that originally was generating random forests in Python, but decided to use R packages used in other studies

library(tidyverse)
library(randomForest)
library(caret)
library(rpart)
library(rpart.plot)
library(sf)
library(mltools)
library(data.table)
library(dplyr)
library(lubridate)

#############################################
# INITIALIZATION
#############################################

# _______________________________________________________________________________________________________________
# Load configuration
config <- config::get(file = "./random_forest/config.yml")
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
    as.data.frame()  # Ensure the output is a data frame
}

sigs_train_path <- file.path(home_dir, config$paths$train$signatures)
sigs_train <- load_signatures(sigs_train_path)


# Attributes
attrs_train_path <- file.path(home_dir, config$paths$train$attributes)
attrs_train <- read_csv(attrs_train_path)

attrs_test_path <- file.path(home_dir, config$paths$test$attributes)
attrs_test <- read_csv(attrs_test_path)


#############################################
# EXECUTION
#############################################

# _______________________________________________________________________________________________________________
# Random forest initialization

set.seed(config$settings$seed)

# define repeated cross-validation with 10 folds and three repeats
# allow for parameter tuning, for mtry grid; range through the total number of predictor variables
max_mtry <- ncol(attrs_train) - 1  # assuming `attrs_train` includes only predictors and one response column
hyper_grid <- expand.grid(mtry = 1:max_mtry)

kfold_cv <- trainControl(method = "cv", number = config$settings$num_folds, search = "grid", verboseIter = TRUE)

out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()

for(sig in config$sigs_predict){
  
  print(paste0("Processing:", sig))
  
  # _______________________________________________________________________________________________________________
  # TRAINING
  train_data <- attrs %>%
    left_join(sigs %>% select(gauge_id, sig), by = "gauge_id") %>%
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
    metric = "RMSE",
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
  # Save the model to a file
  
  # append r2 value
  out_r2[[sig]] <- mean(forest$finalModel$rsq)
  
  # Append to larger output list, variable importance
  out_var_importance[[sig]] <- importance(forest$finalModel, type = 1, scale = TRUE) %>%
    as.data.frame() %>%
    tibble::rownames_to_column(var = "predictor") %>%
    dplyr::mutate(sig_name = sig)
  
  
  # _______________________________________________________________________________________________________________
  # TEST
  # Predict signature value for new samples
  test_data <- attrs_test %>%
    select(-gauge_id)
  
  predictions <- predict(forest, test_data)
  
  # Store predictions in the list
  out_sig_predictions[[sig]] <- data.frame(gauge_id = attrs_test$gauge_id, prediction = predictions, sig_name = sig)
  
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