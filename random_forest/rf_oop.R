library(R6)
library(config)
library(randomForest)
library(caret)
library(dplyr)
library(readr)
library(tidyr)

RandomForestModel <- R6Class("RandomForestModel",
                             public = list(
                               config = NULL,
                               data = NULL,
                               model = NULL,
                               
                               initialize = function(config_file) {
                                 self$config <- config::get(file = config_file)
                               },
                               
                               load_data = function() {
                                 
                                 signature_path <- paste0(self$config$paths$home_dir, self$config$paths$input$signatures)
                                 attribute_path <- paste0(self$config$paths$data_dir, self$config$paths$input$attributes)
                                 
                                 self$data <- list(
                                   sigs = read.csv(signature_path, colClasses = c(gauge_id = "character")),
                                   attrs = read.csv(attribute_path, colClasses = c(gauge_id = "character"))
                                 )
                                 
                                 self$data$sigs <- self$data$sigs %>%
                                   select(gauge_id, TotalRR, RR_Seasonality, EventRR, Recession_a_Seasonality,
                                          AverageStorage, RecessionParameters_a, RecessionParameters_b, RecessionParameters_c,
                                          First_Recession_Slope, Mid_Recession_Slope, EventRR_TotalRR_ratio,
                                          VariabilityIndex, BFI, BFI_90, BaseflowRecessionK) %>%
                                   as.data.frame()
                                 
                               },
                               
                               train_model = function() {
                                 set.seed(self$config$settings$seed)
                                 self$model <- randomForest(
                                   TotalRR ~ ., data = self$data$sigs,
                                   ntree = self$config$settings$ntree, importance = TRUE
                                 )
                               },
                               
                               save_results = function() {
                                 write.csv(self$model$predicted, self$config$paths$output$predictions, row.names = FALSE)
                                 write.csv(importance(self$model), self$config$paths$output$import, row.names = FALSE)
                                 write.csv(self$model$rsq, self$config$paths$output$rsquared, row.names = FALSE)
                               }
                             )
)

# Usage
rf_model <- RandomForestModel$new(config_file = "config.yml")
rf_model$load_data()
rf_model$train_model()
rf_model$save_results()
