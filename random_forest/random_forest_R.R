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

#############################################
# INITIALIZATION
#############################################

# _______________________________________________________________________________________________________________
# Load configuration
config <- config::get(file = "./random_forest/config.yml")

# Configs
home_dir <- file.path("G:", "Shared drives", "Signatures -- large scale", "baseflow", "RAraki")

# _______________________________________________________________________________________________________________
# Load data

# Define a function to load and process the signature data
load_signatures <- function(file_path) {
  data <- read.csv(file_path, stringsAsFactors = FALSE)
  selected_columns <- config$columns
  data %>%
    select(all_of(selected_columns)) %>%
    as.data.frame()
}


# Signature
sigs_train_path <- file.path(home_dir, "out", "signatures", "caravan_camels_20240609", "out_calc_ALL_custom.csv")
sigs_train <- load_signatures(sigs_train_path)

sigs_test_path <- file.path(home_dir, "out", "signatures", "caravan_camels_20240609", "out_calc_ALL_custom.csv")
sigs_test <- load_signatures(sigs_test_path)


# Attributes
attrs_train_path <- file.path(home_dir, "data", "Caravan1.4", "attributes", "camels", "attributes_caravan_camels.csv")
attrs_train = read_csv(attrs_train_path)

attrs_test_path <- file.path(home_dir, "data", "Caravan1.4", "attributes", "camels", "attributes_caravan_camels.csv")
attrs_test = read_csv(attrs_test_path)

#############################################
# EXECUTION
#############################################

# _______________________________________________________________________________________________________________
# Random forest initialization
sig <- 'BFI'
set.seed(0)

out_r2 <- list()
out_var_importance <- list()
out_sig_predictions <- list()


# _______________________________________________________________________________________________________________
# TRAINING
train_data = attrs %>% 
  left_join(sigs %>% select(gauge_id, sig), by = "gauge_id") %>% 
  select(-gauge_id) %>% 
  drop_na()

# define repeated cross-validation with 10 folds and three repeats
# allow for parameter tuning, for mtry grid; range through the total number of predictor variables
hyper_grid <- expand.grid(
  mtry = c(1)
)

tenfold_cv <- trainControl(method = 'cv', number = 10, search = "grid", verboseIter = TRUE)

forest <- train(
  # signature to predict
  formula(paste(sig, "~ .")),
  # input attribute dataset, includes signature
  data = train_data,
  # Random forest method
  method = 'rf',
  # metric to evaluate model performance
  metric = 'MSE',
  # Number of trees
  # adding the repeated cross validation
  trControl = tenfold_cv,
  ntree = 500,
  # hyperparameter testing
  tuneGrid = hyper_grid,
  # return importance, want %IncMSE data
  importance = TRUE
)

print(forest)
print(forest$finalModel)

# _______________________________________________________________________________________________________________
# Save the model to a file
saveRDS(forest, "rf_model.rds")


# _______________________________________________________________________________________________________________
# Save the model to a file

# append r2 value 
out_r2[[sig]] =mean(forest$finalModel$rsq)

# Append to larger output list, variable importance
out_var_importance[[sig]] <- importance(forest$finalModel, type = 1, scale = TRUE) %>%
  as.data.frame() %>%
  tibble::rownames_to_column(var = "predictor") %>%
  dplyr::mutate(signature = sig)

  
# _______________________________________________________________________________________________________________
# TEST
# Predict signature value for new samples
test_data <- rf_input_attribs_new %>%
  select(-gauge_id)

predictions <- predict(forest, test_data)

# Store predictions in the list
out_sig_predictions[[sig]] <- data.frame(gauge_id = rf_input_attribs_new$gauge_id, prediction = predictions, signature = sig)




# _______________________________________________________________________________________________________________
#############################################
# FINALIZE
#############################################

# Output the results
all_sig_predictions = bind_rows(out_sig_predictions)
all_var_importance <- bind_rows(out_var_importance)
all_r2 = bind_rows(out_r2) %>%
  pivot_longer(everything(), names_to = "signature", values_to = "r_squared")

write.csv(all_sig_predictions, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/caravan_geol_giw_predicted_signatures.csv",
          row.names = FALSE)

write.csv(all_var_importance, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/caravan_geol_giw_var_importance.csv",
          row.names = FALSE)

write.csv(all_r2, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/caravan_geol_giw_r_squared.csv",
          row.names = FALSE)
