# ============================================================================
# R Script for Signature and Attribute Visualization with Partial Dependence
# Translated from Python with added SHAP and variable importance plots
# ============================================================================

# Load required libraries
library(tidyverse)
library(ggplot2)
library(maps)
library(sf)
library(randomForest)
library(iml)
library(plotly)
library(gridExtra)
library(viridis)
library(jsonlite)
library(yaml)

# ============================================================================
# CONFIGURATION
# ============================================================================

sig_name <- "BFI"
cluster_num <- 0
exp_date <- "20250715"

# ============================================================================
# LOAD DATA
# ============================================================================

# Set up paths
gdrive_dir <- "G:/Shared drives/Signatures -- large scale/baseflow/RAraki"
attrs_file <- file.path(
    gdrive_dir,
    "data/derived_attrs/assembled_RA/attrs_cara_gages2_etc_20250517+cluster.csv"
)
# Load data
attrs_df <- read.csv(attrs_file, stringsAsFactors = FALSE)

# Load signature data
sig_file <- file.path(
    gdrive_dir,
    "out/signatures/caravan_us_20250525/out_calc_All_custom_filt_qc_snow_area.csv"
)
sig_df <- read.csv(sig_file, stringsAsFactors = FALSE)

# Load model config
model_config_file <- file.path(model_dir, "config_train.yaml")
model_config <- read_yaml(model_config_file)

# Join data
print(model_config$attrs_of_interest)

train_data <- attrs_df %>%
    inner_join(sig_df, by = "gauge_id") %>%
    {
        if (cluster_num != "all") filter(., cluster == cluster_num) else .
    } %>%
    select(
        gauge_id,
        all_of(model_config$attrs_of_interest),
        all_of(sig_name)
    ) %>%
    drop_na()
print(train_data)

# Cluster info
cluster_info_file <- "C:/Users/flipl/dev/signature-prediction/random_forest/visualize/plot_config_expcolors_clusters.json"
cluster_info <- fromJSON(cluster_info_file)


# Load model
model_dir <- file.path(
    gdrive_dir,
    paste0(
        "out/rf/output_raraki_",
        exp_date,
        "_cluster_",
        cluster_num
    )
)

# Load trained model
model_file <- file.path(model_dir, paste0("model_", sig_name, ".rds"))
if (file.exists(model_file)) {
    trained_model <- readRDS(model_file)
    message(paste("Loaded model for", sig_name))
} else {
    message(paste("Model file not found:", model_file))
    trained_model <- NULL
}

# Load variable importance if available
var_importance_file <- file.path(model_dir, "var_importance.csv")
if (file.exists(var_importance_file)) {
    var_importance <- read.csv(
        var_importance_file,
        stringsAsFactors = FALSE
    ) %>%
        filter(sig_name == !!sig_name) %>%
        arrange(desc(X.IncMSE))
    message("Loaded variable importance data")
} else {
    message("Variable importance file not found")
    var_importance <- NULL
}


# ============================================================================
# PARTIAL DEPENDENCE PLOTS
# ============================================================================

library(pdp)
library(caret)

attr_name <- "geol_weighted_ave_age_ma"

# For caret models, you don't need to specify the train parameter
pdp_result <- partial(trained_model, pred.var = attr_name)
plotPartial(pdp_result, ylab = sig_name)

# pdp_result <- partial(trained_model, pred.var = attr_name, train = train_data)
# plotPartial(pdp_result)

# ============================================================================
# SECOND METHOD - IML Package
# ============================================================================

library(iml)
library(ggplot2)

# Create predictor object
predictor <- Predictor$new(
    trained_model,
    data = train_data[, -which(names(train_data) == sig_name)],
    y = train_data[[sig_name]] # Fixed: use [[ ]] for column access
)

# For feature effects (similar to dependence plots)
feature_effect <- FeatureEffect$new(
    predictor,
    feature = attr_name,
    method = "pdp"
)
plot(feature_effect)
