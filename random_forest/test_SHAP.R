# Script to load trained Random Forest models and plot SHAP values
# This script loads .rds model files generated from train_main_mp.R and creates SHAP visualizations

# Required libraries
library(tidyverse)
library(randomForest)
library(caret)
library(iml)
library(ggplot2)
library(gridExtra)
library(viridis)
library(RColorBrewer)

#############################################
# CONFIGURATION
#############################################

# Set paths - modify these according to your setup
model_dir <- "G:/Shared drives/Signatures -- large scale/baseflow/RAraki/out/rf/output_flipl_20250709_test_SHAP"  # Directory containing .rds model files
attributes_file <- "G:/Shared drives/Signatures -- large scale/baseflow/RAraki/data/derived_attrs/assembled_RA/attrs_cara_gages2_etc_20250517+cluster_copy_for_shap.csv"    # Attributes file used for training
output_dir <- "G:/Shared drives/Signatures -- large scale/baseflow/RAraki/out/rf/output_flipl_20250709_test_SHAP"         # Directory to save plots

# Create output directory if it doesn't exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
  message("Created output directory: ", output_dir)
}

# Signature names to analyze (modify based on your models)
sig = "geol_weighted_ave_age_ma_copy"  # Add your signature names here


#############################################
# HELPER FUNCTIONS
#############################################

# Function to load a trained model
load_model <- function(model_path) {
  if (file.exists(model_path)) {
    model <- readRDS(model_path)
    message("Loaded model: ", basename(model_path))
    return(model)
  } else {
    message("Model file not found: ", model_path)
    return(NULL)
  }
}

#############################################
# MAIN EXECUTION
#############################################

# Load attributes data
message("Loading attributes data...")
attributes_data <- read.csv(attributes_file, stringsAsFactors = FALSE)
message("Loaded attributes data with ", nrow(attributes_data), " rows and ", ncol(attributes_data), " columns")

# Initialize lists to store results
models <- list()
shap_data_list <- list()
summary_plots <- list()
dependence_plots <- list()

# Process each signature

message("\nProcessing signature: ", sig)

# Load model
model_path <- file.path(model_dir, paste0("model_", sig, ".rds"))
model <- load_model(model_path)

if (is.null(model)) {
  message("Skipping ", sig, " - model not found")
  next
}

models[[sig]] <- model

# Calculate SHAP values
message("Calculating SHAP values for ", sig)

# Prepare data (remove signature column and gauge_id if present)
feature_data <- attributes_data %>%
  select(-any_of(c("gauge_id", "cluster"))) %>%
  drop_na()

predictor_names <- names(model$trainingData) %>% 
  setdiff(".outcome")  # Remove .outcome from the list

# Add the signature column to the selection
columns_to_select <- c(predictor_names, sig)

feature_data <- feature_data %>%
  select(all_of(columns_to_select)) %>%
  drop_na()


print(feature_data)
print(length(feature_data))

# Remove infinite values
feature_data <- feature_data %>%
  mutate(across(where(is.numeric), ~ifelse(is.infinite(.), NA, .))) %>%
  drop_na()


x <- feature_data %>%
  select(-sig)

print(x)
print(length(x))

# Create predictor object
predictor <- Predictor$new(
  model$finalModel, 
  data = x,
  y = feature_data[sig]
)

options(future.globals.maxSize = 1000 * 1024^2) 
imp <- FeatureImp$new(predictor, loss = "mae")
library("ggplot2")
plot(imp)


available_features <- names(x)
print("Available features:")
print(available_features)

ale <- FeatureEffect$new(predictor, feature = "ARIDITY_GAGES2", grid.size = 100)
ale$plot()

interact <- Interaction$new(predictor, grid.size = 15)
plot(interact)

effs <- FeatureEffects$new(predictor, grid.size = 10)
plot(effs)

shapley <- Shapley$new(predictor, x.interest = x[1, ])
shapley$plot()

shapley$explain(x.interest = x[2, ])
shapley$plot()



# Loop through multiple rows to calculate SHAP values
num_rows_to_analyze <- min(10, nrow(x))  # Analyze first 10 rows or all rows if less than 10
message("Calculating SHAP values for ", num_rows_to_analyze, " observations...")


# # Simple parallelization using parallel package
# library(parallel)

# # Detect number of cores (use all available cores minus 1)
# num_cores <- detectCores() - 1
# message("Using ", num_cores, " cores for parallel SHAP calculation")

# set.seed(0)

# # Define function to calculate SHAP for a single observation
# calculate_shap_single <- function(i, predictor, x) {
#   shapley <- iml::Shapley$new(predictor, x.interest = x[i, ])
#   results <- shapley$results
#   results$predicted_value <- shapley$y.hat.interest
#   results$sample_num <- i
#   return(results)
# }

# # Parallel computation
# num_samples <- 10  # Change this to nrow(x) for all samples
# system.time({
#   # Use mclapply for parallel processing (Unix/Mac) or parLapply for Windows
#   if (.Platform$OS.type == "unix") {
#     # For Unix/Mac systems
#     shap_values <- mclapply(1:num_samples, 
#                            calculate_shap_single, 
#                            predictor = predictor, 
#                            x = x,
#                            mc.cores = num_cores)
#   } else {
#     # For Windows systems
#     cl <- makeCluster(num_cores)
#     clusterEvalQ(cl, library(iml))
#     clusterExport(cl, c("predictor", "x"), envir = environment())
    
#     shap_values <- parLapply(cl, 1:num_samples, 
#                             calculate_shap_single, 
#                             predictor = predictor, 
#                             x = x)
#     stopCluster(cl)
#   }
  
#   # Combine results
#   data_shap_values <- dplyr::bind_rows(shap_values)
# })

# data_shap_values <- data_shap_values %>%
#   mutate(
#     # Extract just the numeric value from "FEATURE_NAME=VALUE" format
#     feature_value = as.numeric(gsub(".*=", "", feature.value))
#     predicted_sig = sig
#   )

# # Save to CSV
# csv_filename <- file.path(output_dir, paste0("shapley_multiple_obs_", sig, "_par.csv"))
# write.csv(data_shap_values, csv_filename, row.names = FALSE)
# message("Saved SHAP values for multiple observations to: ", csv_filename)
# 
# message("Parallel SHAP calculation completed with ", nrow(data_shap_values), " total results")
# data_shap_values

# Initialize list to store all SHAP results
all_shapley_results <- list()

# Initialize shapley object outside the loop
shapley <- NULL


# Loop through rows
for (i in 1:num_rows_to_analyze) {
  message("Processing observation ", i, " of ", num_rows_to_analyze)
  
  tryCatch({
    if (i == 1) {
      # Create SHAP object for the first observation
      shapley <- Shapley$new(predictor, x.interest = x[i, ])
    } else {
      # Reuse existing shapley object for subsequent observations
      shapley$explain(x.interest = x[i, ])
    }
      
    # Get results and add observation index
    results <- shapley$results
    results$observation_id <- i
    results$sig_name <- sig
    
    # Store results
    all_shapley_results[[i]] <- results
    
  }, error = function(e) {
    message("Error processing observation ", i, ": ", e$message)
    # Create empty result for this observation
    all_shapley_results[[i]] <- data.frame(
      feature = character(0),
      phi = numeric(0),
      phi.var = numeric(0),
      feature.value = character(0),
      observation_id = integer(0),
      sig_name = character(0)
    )
  })
}

# Combine all results into one dataframe
if (length(all_shapley_results) > 0) {
  combined_shapley <- bind_rows(all_shapley_results)
  
      combined_shapley <- combined_shapley %>%
      mutate(
        # Extract just the numeric value from "FEATURE_NAME=VALUE" format
        feature_value = as.numeric(gsub(".*=", "", feature.value))
      )
  
  # Save to CSV
  csv_filename <- file.path(output_dir, paste0("shapley_multiple_obs_", sig, ".csv"))
  write.csv(combined_shapley, csv_filename, row.names = FALSE)
  message("Saved SHAP values for multiple observations to: ", csv_filename)
  
  # Print summary
  message("Summary:")
  message("- Total observations processed: ", length(all_shapley_results))
  message("- Total SHAP values calculated: ", nrow(combined_shapley))
  message("- Features analyzed: ", length(unique(combined_shapley$feature)))
  
  # Show first few results
  print("First few SHAP results:")
  print(head(combined_shapley, 10))
  
} else {
  message("No SHAP results to save")
}

combined_shapley

message("Analysis complete! Check the output directory for plots and report.")
message("Output directory: ", output_dir)

print(combined_shapley)
