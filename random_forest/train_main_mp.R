# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

# ____________________________________________________________
# To run this script in Windows:
# > cd signature-prediction\random_forest
# > train_run.bat

# To run this script in Linux:
# > cd signature-prediction/random_forest
# > train_run.sh

# ____________________________________________________________
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

# ____________________________________________________________
# Package imports

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

# ____________________________________________________________
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
out_path <- file.path(
  home_dir,
  config$paths$out_dir,
  paste0(
    "output_",
    username,
    "_",
    formatted_datetime,
    "_",
    config$experiment_name
  )
)
if (!dir.exists(out_path)) {
  dir.create(out_path, recursive = TRUE)
  message("Directory created: ", out_path)
} else {
  message("Directory already exists.")
}
print(config$experiment_name)

# Start the timer
start_time <- proc.time()


# ____________________________________________________________
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

# Define a function to load and process the attributes data
load_attrs <- function(file_path) {
  # Read the data from the specified file path
  data <- read.csv(file_path, stringsAsFactors = FALSE)

  # Select the gauge_id and the attributes of interest
  # Include cluster column only if it exists
  columns_to_select <- c("gauge_id", config$attrs_of_interest)
  if ("cluster" %in% names(data)) {
    columns_to_select <- c(columns_to_select, "cluster")
  }

  data %>%
    select(all_of(columns_to_select)) %>%
    as.data.frame()
}

print("Loading training attributes")
attrs_train_path <- file.path(home_dir, config$paths$train$attributes)
attrs_train <- load_attrs(attrs_train_path)

print("Loading test attributes")
attrs_test_path <- file.path(home_dir, config$paths$test$attributes)
attrs_test <- load_attrs(attrs_test_path)


# ____________________________________________________________
# If running the model by cluster, filter and get the subset of the data
print("Filtering by cluster")
if (config$filter_by_cluster$run) {
  attrs_train <- attrs_train %>%
    filter(cluster == config$filter_by_cluster$name) %>%
    select(-cluster)
  attrs_test <- attrs_test %>%
    filter(cluster == config$filter_by_cluster$name) %>%
    select(-cluster)
  message(
    "Selected ",
    nrow(attrs_train),
    " gauges in: ",
    config$filter_by_cluster$name
  )
} else {
  # Remove cluster column if it exists
  if ("cluster" %in% names(attrs_train)) {
    attrs_train <- attrs_train %>%
      select(-cluster)
  }
  if ("cluster" %in% names(attrs_test)) {
    attrs_test <- attrs_test %>%
      select(-cluster)
  }
}

#############################################
# EXECUTION
#############################################

# ____________________________________________________________
# Parallel pool setup
print("initiating parallel pool")

# Set up parallel backend for caret
num_cores <- min(config$parallel$num_cores, detectCores())
cl <- makeCluster(num_cores)
registerDoParallel(cl)
print(paste("Using", num_cores, "cores for parallel processing"))


# ____________________________________________________________
# Random forest initialization
set.seed(config$settings$seed)

# Set up basic training control parameters
num_folds <- config$settings$num_folds

# Calculate number of predictors (same for all signatures)
num_predictors <- ncol(attrs_train) - 1 # minus gauge_id column
message(paste("Using", num_predictors, "predictors for all signatures"))

# Create hyperparameter grid based on actual number of predictors
hyper_grid <- expand.grid(
  mtry = c(1:num_predictors)
)

# Set up properly structured seeds for reproducibility
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
  allowParallel = TRUE # Enable parallel within caret
)

# Prepare output list
out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()
out_shap_values <- list()
results <- list()

# ____________________________________________________________
# Process each signature
print("Start training multiple Random Forest models")


for (sig in config$sigs_predict) {
  tryCatch(
    {
      message(paste("Processing signature:", sig))

      # ____________________________________________________________
      # PREPARE TRAINING DATA

      train_data <- attrs_train %>%
        inner_join(
          sigs_train %>% select(gauge_id, all_of(sig)),
          by = "gauge_id"
        ) %>%
        select(-gauge_id) %>%
        drop_na() %>%
        filter_all(all_vars(!is.infinite(.)))

      message(paste("Data has", nrow(train_data), "rows"))

      # Check for any problematic values before proceeding
      na_count_before <- sum(is.na(train_data))
      inf_count_before <- sum(sapply(train_data, function(x) {
        sum(is.infinite(x), na.rm = TRUE)
      }))
      nan_count_before <- sum(sapply(train_data, function(x) {
        sum(is.nan(x), na.rm = TRUE)
      }))

      if (na_count_before > 0 || inf_count_before > 0 || nan_count_before > 0) {
        message(paste(
          "Found problematic values before cleaning:",
          na_count_before,
          "NAs,",
          inf_count_before,
          "Inf values,",
          nan_count_before,
          "NaN values"
        ))

        # Replace NaN with NA
        train_data <- train_data %>%
          mutate(across(where(is.numeric), ~ ifelse(is.nan(.), NA, .)))

        # Filter out infinite values
        train_data <- train_data %>%
          mutate(across(where(is.numeric), ~ ifelse(is.infinite(.), NA, .))) %>%
          drop_na() # Drop rows with any NA values again

        # Count remaining values after cleaning
        na_count_after <- sum(is.na(train_data))
        inf_count_after <- sum(sapply(train_data, function(x) {
          sum(is.infinite(x), na.rm = TRUE)
        }))
        nan_count_after <- sum(sapply(train_data, function(x) {
          sum(is.nan(x), na.rm = TRUE)
        }))

        message(paste(
          "After cleaning:",
          nrow(train_data),
          "rows remain with",
          na_count_after,
          "NAs,",
          inf_count_after,
          "Inf values,",
          nan_count_after,
          "NaN values"
        ))
      }

      # Ensure a numeric target for regression
      train_data[[sig]] <- as.numeric(train_data[[sig]])

      # ____________________________________________________________
      # TRAINING MODEL

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

      # ____________________________________________________________
      # Predict signature values
      test_data <- attrs_test %>%
        drop_na()

      predictions <- predict(forest, test_data %>% select(-gauge_id))

      # ____________________________________________________________
      # Append results

      # append r2 value
      out_r2 <- data.frame(
        sig_name = sig,
        r_squared = tail(forest$finalModel$rsq, 1)
      )

      # append variable importance
      out_var_importance <- importance(
        forest$finalModel,
        type = 1,
        scale = TRUE
      ) %>%
        as.data.frame() %>%
        tibble::rownames_to_column(var = "predictor") %>%
        dplyr::mutate(sig_name = sig)

      # append predicted signature values
      out_sig_predictions <- data.frame(
        gauge_id = test_data$gauge_id,
        prediction = predictions,
        sig_name = sig
      )

      # ____________________________________________________________
      # Calculate SHAP values for the signature
      # https://cran.r-project.org/web/packages/iml/vignettes/intro.html
      # https://christophm.github.io/interpretable-ml-book/agnostic.html

      # Create a predictor object for the model
      # "data" should be the training data (attributes) without the signature column
      # "y" should be the signature column

      # Unclear how many samples to use for SHAP values
      # num_rows_to_analyze <- min(config$settings$shap_rows, nrow(train_data))

      # Use all rows for SHAP values for now
      num_rows_to_analyze <- nrow(train_data)

      x_train_interest <- train_data %>% select(-all_of(sig))
      y_train_interest <- train_data[[sig]]

      # Calculate SHAP values in parallel
      message(paste(
        "Calculating SHAP values for",
        num_rows_to_analyze,
        "observations in parallel for signature",
        sig
      ))

      shap_values <- foreach(
        i = 1:num_rows_to_analyze,
        .combine = "c",
        .packages = c("iml", "dplyr")
      ) %dopar%
        {
          {
            # Each worker creates its own predictor and shapley object
            worker_predictor <- Predictor$new(
              forest$finalModel,
              data = x_train_interest,
              y = y_train_interest
            )

            # Create SHAP object for this observation
            shapley <- Shapley$new(
              worker_predictor,
              x.interest = x_train_interest[i, ]
            )

            # Get results and add observation index
            shap_results <- shapley$results
            shap_results$observation_id <- i
            shap_results$sig_name <- sig

            # Return results
            list(shap_results)
          }
        }

      # Store SHAP values in the list
      out_shap_values <- bind_rows(shap_values) %>%
        dplyr::mutate(
          feature = gsub("=.*", "", feature),
          feature_value = as.numeric(gsub(".*=", "", feature.value)),
          sig_name = sig
        ) %>%
        select(observation_id, feature, phi, phi.var, feature_value, sig_name)

      # ____________________________________________________________
      # Save the trained model for this signature
      if (config$save_models) {
        model_file_name <- file.path(out_path, paste0("model_", sig, ".rds"))
        saveRDS(forest, model_file_name)
        message(paste("Saved model for", sig, "to", model_file_name))
      }

      # ____________________________________________________________
      # Store results for this signature
      results[[sig]] <- list(
        sig_predictions = out_sig_predictions,
        r2 = out_r2,
        var_importance = out_var_importance,
        shap_values = out_shap_values
      )
    },
    error = function(e) {
      message(paste("Model training error for signature", sig, ":", e$message))
      # Return placeholders if an error occurs
      results[[sig]] <- list(
        sig_predictions = data.frame(
          gauge_id = attrs_test$gauge_id,
          prediction = NA,
          sig_name = sig
        ),
        r2 = data.frame(sig_name = sig, r_squared = NA),
        var_importance = data.frame(
          predictor = names(attrs_train)[names(attrs_train) != "gauge_id"],
          Importance = NA,
          sig_name = sig
        ),
        shap_values = data.frame(
          observation_id = integer(0),
          feature = character(0),
          phi = numeric(0),
          phi.var = numeric(0),
          feature_value = numeric(0),
          sig_name = character(0)
        )
      )
    }
  )
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
write.csv(
  all_sig_predictions,
  file.path(out_path, "predicted_signatures_train.csv"),
  row.names = FALSE
)
write.csv(
  all_var_importance,
  file.path(out_path, "var_importance.csv"),
  row.names = FALSE
)
write.csv(all_r2, file.path(out_path, "r_squared.csv"), row.names = FALSE)
write.csv(
  all_shap_values,
  file.path(out_path, "shap_values.csv"),
  row.names = FALSE
)

print("Saving config file")
# Save config file
yaml::write_yaml(config, file.path(out_path, "config_train.yaml"))

# ______________________________________________________
# Calculate execution time
end_time <- proc.time()
execution_time <- end_time - start_time
print(paste("Total Execution Time: ", execution_time[3], "seconds"))
print(paste("Output results to", out_path))
