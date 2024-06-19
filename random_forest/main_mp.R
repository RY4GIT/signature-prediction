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
library(doParallel)
library(foreach)

#############################################
# INITIALIZAT
#############################################

# _______________________________________________________________________________________________________________
# Load configuration
#############################################
# Change here to select which config to read
Sys.setenv(R_CONFIG_ACTIVE = "reproduce_aholt") # "default", "reproduce_aholt"
#############################################
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

# # Before the loop, open a connection to a log file
# log_file <- file(file.path(out_path, "log.txt"), open = "wt")

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
    as.data.frame() # Ensure the output is a data frame
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
    select(gauge_id, all_of(config$attrs_of_interest)) %>%
    as.data.frame()
}

attrs_train_path <- file.path(home_dir, config$paths$train$attributes)
attrs_train <- load_attrs(attrs_train_path)

attrs_test_path <- file.path(home_dir, config$paths$test$attributes)
attrs_test <- load_attrs(attrs_test_path)

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

out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()

hyper_grid <- expand.grid(
  mtry = c(1:(length(attrs_train)-1))
)

kfold_cv <- trainControl(method = "cv", number = config$settings$num_folds, search = "grid", verboseIter = TRUE)

print("Start multiple RFs")

results <- foreach(sig = config$sigs_predict, .packages = c("randomForest", "dplyr", "tidyr", "caret", "purrr")) %dopar% {
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
    left_join(sigs_train %>% select(gauge_id, sig), by = "gauge_id") %>%
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
    # hyperparameter testing
    tuneGrid = hyper_grid,
    # return importance, want %IncMSE data
    importance = TRUE
  )

  print(forest)
  print(forest$finalModel)

  # _______________________________________________________________________________________________________________
  # Predict signature value / can be on a test dataset. Currently it is used to simply get predicted signature values from training & validation
  test_data <- attrs_test %>%
    drop_na() 
  
  predictions <- predict(forest, test_data%>%select(-gauge_id))
# 
#   log_messages <- c(log_messages, "Completed processing for signature.")
#   
  
  # _______________________________________________________________________________________________________________
  # Collect results for CSV
  
  # append r2 value
  if(length(forest$finalModel$rsq) == 0) {
    out_r2 <- data.frame(sig_name = sig, r_squared = NA)  # Use NA when no r_squared value is calculated
  } else {
    out_r2 <- data.frame(sig_name = sig, r_squared = mean(forest$final$rsq))
  }
  
  # Append to larger output list, variable importance
  if(nrow(importance(forest$finalModel, type = 1, scale = TRUE)) == 0) {
    out_var_importance <- data.frame(predictor = NA, Importance = NA, sig_name = sig)
  } else {
    out_var_importance <- importance(forest$finalModel, type = 1, scale = TRUE) %>%
      as.data.frame() %>%
      tibble::rownames_to_column(var = "predictor") %>%
      dplyr::mutate(sig_name = sig)
  }
  
  if(length(predictions) == 0) {
    out_sig_predictions <- data.frame(gauge_id = NA, prediction = NA, sig_name = sig)
  } else {
    out_sig_predictions <- data.frame(gauge_id = test_data$gauge_id, prediction = predictions, sig_name = sig)
  }
  
  list(
    sig_predictions = out_sig_predictions, 
    r2 = out_r2,
    var_importance = out_var_importance
  )
}

# _______________________________________________________________________________________________________________
#############################################
# FINALIZE
#############################################

# Unlist results appropriately
out_sig_predictions <- lapply(results, `[[`, "sig_predictions")
out_r2 <- lapply(results, `[[`, "r2")
out_var_importance <- lapply(results, `[[`, "var_importance")

# Combine lists into data frames
all_sig_predictions <- bind_rows(out_sig_predictions)
all_var_importance <- bind_rows(out_var_importance)
all_r2 <- bind_rows(out_r2)

write.csv(all_sig_predictions, file.path(out_path, "predicted_signatures.csv"), row.names = FALSE)
write.csv(all_var_importance, file.path(out_path, "var_importance.csv"), row.names = FALSE)
write.csv(all_r2, file.path(out_path, "r_squared.csv"), row.names = FALSE)

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

# close(log_file)

# Stop the parallel backend when done
stopImplicitCluster()
