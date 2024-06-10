# script for plotting random forest model outputs

library(tidyverse)
library(cowplot)

# CAMELS attribute datasets

### OLD VERSIONS ####
# Addor 2018
# rf_camels_addor_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_addor_var_importance.csv")
# rf_camels_addor_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_addor_r_squared.csv")


# version 2: Addor, and no categorical variables (dom land cover, dom lithology)
rf_camels_v2_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_var_importance.csv")
rf_camels_v2_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_r_squared.csv")


# rf_camels_v2_geol_av_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_av_var_importance.csv")
# rf_camels_v2_geol_av_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_av_r_squared.csv")
# rf_camels_v2_giw_frac_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_giw_frac_var_importance.csv")
# rf_camels_v2_giw_frac_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_giw_frac_r_squared.csv")

# rf_camels_v2_new_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_var_importance.csv")
# rf_camels_v2_new_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_r_squared.csv")

# version 2, but only in Northeastern forest region; with and without new attributes
# rf_camels_v2_northfor_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_northwestfor_var_importance.csv")
# rf_camels_v2_northfor_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_northwestfor_r_squared.csv")
# rf_camels_v2_easttemp_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_easttemp_var_importance.csv")
# rf_camels_v2_easttemp_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_easttemp_r_squared.csv")
# rf_camels_v2_greatplains_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_greatplains_var_importance.csv")
# rf_camels_v2_greatplains_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_greatplains_r_squared.csv")
# 
# 
# rf_camels_v2_new_northfor_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_northwestfor_var_importance.csv")
# rf_camels_v2_new_northfor_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_northwestfor_r_squared.csv")
# rf_camels_v2_new_easttemp_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_easttemp_var_importance.csv")
# rf_camels_v2_new_easttemp_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_easttemp_r_squared.csv")
# rf_camels_v2_new_greatplains_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_greatplains_var_importance.csv")
# rf_camels_v2_new_greatplains_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v2_geol_giw_greatplains_r_squared.csv")

# # version 3: removing variables with correlation greater than 0.7 before modeling
# rf_camels_v3_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_var_importance.csv")
# rf_camels_v3_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_r_squared.csv")
# rf_camels_v3_geol_av_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_geol_av_var_importance.csv")
# rf_camels_v3_geol_av_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_geol_av_r_squared.csv")
# rf_camels_v3_giw_frac_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_giw_frac_var_importance.csv")
# rf_camels_v3_giw_frac_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_v3_giw_frac_r_squared.csv")
# 
# 
# # CARAVAN attribute datasets
# rf_caravan_v3_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_var_importance.csv")
# rf_caravan_v3_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_r_squared.csv")
# rf_caravan_v3_geol_av_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_geol_av_var_importance.csv")
# rf_caravan_v3_geol_av_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_geol_av_r_squared.csv")
# rf_caravan_v3_giw_frac_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_giw_frac_var_importance.csv")
# rf_caravan_v3_giw_frac_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs/camels_caravan_v3_giw_frac_r_squared.csv")
# 

#### FINAL VERSIONS ####

rf_camels_new_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_aridity_geol_giw_var_importance.csv")
rf_camels_new_east_imp = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_easttemp_northfor_geol_giw_var_importance.csv")

rf_caravan_new_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/caravan_geol_giw_r_squared.csv")
rf_camels_new_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_aridity_geol_giw_r_squared.csv")
rf_camels_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_r_squared.csv")

r_comparison = rf_camels_new_r %>% 
  rename(r_squared_camels_new = r_squared) %>% 
  left_join(rf_caravan_new_r, by = "signature") %>% 
  rename(r_squared_caravan = r_squared) %>% 
  mutate(r_diff = r_squared_caravan - r_squared_camels_new)

rf_easttemp_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_easttemp_northfor_r_squared.csv")
rf_easttemp_new_r = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/camels_easttemp_northfor_geol_giw_r_squared.csv")


r_easttemp_comparison = rf_easttemp_r %>% 
  rename(r_squared_camels = r_squared) %>% 
  left_join(rf_easttemp_new_r, by = "signature") %>% 
  rename(r_squared_new = r_squared) %>% 
  mutate(r_diff = r_squared_new - r_squared_camels)

#### Performance Plotting ####

rf_r_all = rf_camels_r %>% 
  mutate(attrib_version = "camels") %>%
  bind_rows(rf_camels_new_r %>% mutate(attrib_version = "camels_plusnew")) %>%
  bind_rows(rf_caravan_new_r %>% mutate(attrib_version = "caravan_plusnew")) %>% 
  filter(signature != "RecessionParameters_a")


rf_camels_v2_r_all = rf_camels_v2_r %>% 
  mutate(attrib_version = "camels") %>%
  # bind_rows(rf_camels_v2_new_r %>% mutate(attrib_version = "camels_plusnew")) %>% 
  # bind_rows(rf_camels_v2_northfor_r %>% mutate(attrib_version = "camels_northfor")) %>%
  # bind_rows(rf_camels_v2_greatplains_r %>% mutate(attrib_version = "camels_greatplains")) %>%
  bind_rows(rf_camels_v2_easttemp_r %>% mutate(attrib_version = "camels_easttemp")) %>%
  # bind_rows(rf_camels_v2_new_northfor_r %>% mutate(attrib_version = "camels_northfor_plusnew")) %>%
  bind_rows(rf_camels_v2_new_easttemp_r %>% mutate(attrib_version = "camels_easttemp_plusnew")) %>%
  # bind_rows(rf_camels_v2_new_greatplains_r %>% mutate(attrib_version = "camels_greatplains_plusnew")) %>% 
  # filter(signature %in% c('AverageStorage', "BFI", "BFI_90", "BaseflowRecessionK", "TotalRR",
  #                         "Recession_a_Seasonality"))
  filter(signature != "RecessionParameters_a")
  
  filter(signature == "BFI" | signature == "BFI_90")

# rf_camels_v3_r_all = rf_camels_v3_r %>% 
#   mutate(attrib_version = "camels") %>% 
#   bind_rows(rf_camels_v3_geol_av_r %>% mutate(attrib_version = "camels_geol_av")) %>% 
#   bind_rows(rf_camels_v3_giw_frac_r %>% mutate(attrib_version = "camels_giw_frac"))
# 
# rf_caravan_v3_r_all = rf_caravan_v3_r %>% 
#   mutate(attrib_version = "caravan") %>% 
#   bind_rows(rf_caravan_v3_geol_av_r %>% mutate(attrib_version = "caravan_geol_av")) %>% 
#   bind_rows(rf_caravan_v3_giw_frac_r %>% mutate(attrib_version = "caravan_giw_frac"))
# 
# rf_camels_v_caravan = rf_camels_v3_r %>% 
#   mutate(attrib_version = "camels") %>% 
#   bind_rows(rf_caravan_v3_r %>% mutate(attrib_version = "caravan"))
# 
rf_camels = rf_camels_v3_r %>%
  mutate(attrib_version = "camels_v3") %>%
  bind_rows(rf_camels_addor_r %>% mutate(attrib_version = "camels_addor")) %>% 
  bind_rows(rf_camels_v2_r %>% mutate(attrib_version = "camels_v2")) %>% 
  filter(signature %in% c('AverageStorage', "BFI", "BFI_90", "BaseflowRecessionK", "TotalRR",
                          "Recession_a_Seasonality"))

# boxplot, R2 on y axis, signature on x axis
ggplot(rf_r_all, aes(x = signature, y = r_squared, fill = attrib_version)) +
  geom_col(position = "dodge", width = 0.6) +
  labs(
    y = "Mean R2",
    x = NULL,
    title = NULL
  ) +
  scale_y_continuous(limits = c(0, 1)) +
  scale_fill_manual(name = "RF Model Performance", values = c("camels" = "lightgrey", "camels_plusnew" = "grey40",
                                                              "caravan_plusnew" = "darkgrey"))+
  theme_minimal()+
  theme(
    plot.title = element_text(size = 24),
    text = element_text(size = 14),   # Increase text (axis labels, title) size
    axis.text.x = element_text(angle = 45, hjust = 1, size = 14),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 16),
    legend.text = element_text(size = 14),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  )
  # scale_fill_manual(name = "RF Model Performance",  # Changing legend name
  #                   labels = c("Caravan attributes", "plus geol", "plus giw"),
  #                   values = c("green", "orange","blue"))


ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures_final/camels_caravan_r_squared.png", width = 10.5, height = 6, dpi = 300,bg = "white")


# trying slightly different aesthetics
ggplot(rf_performance_r2, aes(x = sig, y = cv_r2)) +
  geom_col(width = 0.6) +  # Adjust the width of the bars
  labs(
    y = "R2",
    x = NULL,
    title = "Model Performance, Cross Validation"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 24),
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.text.y = element_text(size = 14),
    axis.title = element_text(size = 16),  # Adjust axis title size
    legend.position = "none"  # Remove legend
  )


#### Increase MSE ####



importance_plotting = rf_camels_new_east_imp %>% 
  filter(signature != "RecessionParameters_a") %>% 
  # filter(signature %in% c('AverageStorage', "BFI", "BFI_90", "BaseflowRecessionK", "TotalRR",
  #                         "Recession_a_Seasonality")) %>%
  # filter(signature == "BFI") %>%
  mutate(color = case_when(predictor == "geol_av_age_ma" ~ "red",
                           predictor == "giw_frac" ~ "blue", 
                           predictor %in% c("p_mean", "pet_mean", "p_seasonality", "frac_snow", "aridity", "high_prec_freq", 
                                            "high_prec_dur", "low_prec_freq", "low_prec_dur") ~ "darkgrey",
                           TRUE ~ "lightgrey"))
  
  # rf_camels_v2_geol_av_imp %>% 
  # filter(signature %in% c('AverageStorage', "BFI", "BFI_90", "BaseflowRecessionK", "TotalRR",
  #                       "Recession_a_Seasonality"))

  # arrange(signature, desc(X.IncMSE)) %>%  # Arrange data by response variable and %IncMSE in descending order
  # group_by(signature) %>%  # Group data by response variable
  # slice_head(n = 5)



incmse_plot_list <- list()
for (sig in unique(importance_plotting$signature)) {
  # Create ggplot for the current signature
  p <- ggplot(importance_plotting[importance_plotting$signature == sig, ], aes(x = X.IncMSE, y = reorder(predictor, X.IncMSE),
                                                                               fill = color)) +
    geom_bar(stat = "identity") +
    scale_fill_manual(values = c("blue" = "blue","red"= "red", "darkgrey" = "grey45", "lightgrey"= "lightgrey")) +
    labs(x = "%IncMSE", y = NULL) +
    # xlim(0, 35) +
    ggtitle(paste(sig)) +
    # ggtitle(paste(sig, "(Northeastern Forested)")) +
    theme_minimal() +
    theme(legend.position = "none")  # Remove legend for individual plots
  
  # Add the ggplot to the list
  incmse_plot_list[[sig]] <- p
}
incmse_final_plot <- plot_grid(plotlist = incmse_plot_list, ncol = 4)  # Adjust ncol as needed

print(incmse_final_plot)
# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures/rf_camels_v2_geol_giw_bar_incmse.png", width = 10, height = 10, dpi = 300,bg = "white")
# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures_final/rf_camels_geol_giw_eco_BFI_bar_incmse.png", width = 4, height = 4, dpi = 300,bg = "white")
ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures_final/rf_camels_northeast_geol_giw_bar_incmse.png", width = 14, height = 18, dpi = 300,bg = "white")





# attributes
attributes = unique(rf_camels_v2_easttemp_imp$predictor)
desired_order = rev(c("p_mean", "pet_mean", "p_seasonality", "frac_snow", "aridity", "high_prec_freq", 
                  "high_prec_dur", "low_prec_freq", "low_prec_dur", 
                  "elev_mean", "slope_mean", "area_gages2", 
                  "frac_forest", "lai_max", "gvf_max", "root_depth_50", "root_depth_99", "evergreen_needleleaf",
                  "soil_depth_pelletier", "soil_depth_statsgo", "max_water_content", "sand_frac",
                  "silt_frac", "clay_frac", "water_frac", "organic_frac", "other_frac",
                  "carbonate_rocks_frac", "geol_porostiy", "geol_permeability", "igneous_volcanic", "sedimentary_clastic",
                  "sedimentary_carbonate", "metamorphics", "unconsolidated",
                  "geol_av_age_ma",
                  "giw_frac"))

# # updated list of attributes
# desired_order <- rev(c("p_mean", "pet_mean", "frac_snow", "seasonality", "high_prec_freq", "high_prec_dur",
#                        "ele_mt_smn", "slp_dg_sav", 'area',
#                        'for_pc_sse',
#                        "cly_pc_sav", "slt_pc_sav", "soc_th_sav", "kar_pc_sse",
#                        'giw_frac', 'geol_av_age_ma' ))




importance_plotting$predictor <- factor(importance_plotting$predictor, levels = desired_order)


ggplot(importance_plotting, aes(x = signature, y = predictor, fill = X.IncMSE, size = X.IncMSE)) +
  geom_point(shape = 21, color = 'black') +
  # scale_color_viridis_c()+
  scale_fill_gradient2(low = "white",high = "black", name = "IncMSE",
                       midpoint = median(rf_camels_v2_geol_av_imp$X.IncMSE),  limits = c(-2, 40)) +
  scale_size_continuous(range = c(2, 10)) +
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
  ) + # Add plot title
  theme_minimal() +                    # Use a minimal theme
  theme(
    plot.title = element_text(size=24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.title = element_text(size = 14),  # Increase axis title size
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)


ggplot(importance_plotting, aes(x = signature, y = predictor)) +
  geom_point(size = 10) +
  # geom_point(shape = 21, size = 10, color = 'black') +
  # scale_color_viridis_c()+
  # scale_fill_gradient2(low = "white",high = "black", name = "IncMSE",
  #                      midpoint = median(rf_camels_v2_geol_av_imp$X.IncMSE),  limits = c(-2, 40)) +
  # scale_size_continuous(range = c(2, 10)) +
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
  ) + # Add plot title
  theme_minimal() +                    # Use a minimal theme
  theme(
    plot.title = element_text(size=24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.title = element_text(size = 14),  # Increase axis title size
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)

# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures/rf_camels_v2_easttemp_incmse.png", width = 10, height = 8, dpi = 300,bg = "white")


ggplot(importance_plotting, aes(x = X.IncMSE, y = predictor, fill = reorder(predictor, X.IncMSE))) +
  geom_bar(stat = "identity") +
  facet_wrap(~ signature, scales = "free", ncol = 3) +
  labs(x = "%IncMSE", y = "Predictor Variable") +
  ggtitle("Importance of Predictor Variables") +
  theme_minimal()



#### PREDICTED SIGNATURE DISTRIBUTIONS #####
library(sf)
conus <- st_read('E:/SDSU_GEOG/Thesis/Data/US states/conus_states.shp')
hysets_sigs = read.csv("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/outputs_final/caravan_geol_giw_predicted_signatures.csv",
                       colClasses = c(gauge_id = "character")) %>% 
  filter(signature != "RecessionParameters_a")

hysets_poly = st_read('E:/SDSU_GEOG/Thesis/Data/NWI_hysets/nwi_hysets_metrics.shp') %>% 
  select(gauge_id,geometry)
hysets_centroid <- st_centroid(hysets_poly)

hyset_sigs_centroid = hysets_centroid %>% 
  left_join(hysets_sigs, by = "gauge_id")

# ggplot() +
#   geom_sf(data = conus, color = "white", fill = "grey") +  # Plot polygon boundaries, color by variable
#   geom_sf(data = hyset_sigs_centroid, aes(fill = prediction), shape = 21, color = "darkgrey", size = 3, alpha = 1) +
#   scale_fill_distiller(palette = "Spectral", direction = 1, name = NULL)+
#   # scale_fill_gradient(low = "red", high = "blue4") +
#   ggtitle("Signature") +
#   theme_void()+
#   theme(
#     plot.title = element_text(size = 30, hjust = 0.5),  # Adjust title size and centering
#     legend.key.size = unit(2, "lines"),  # Adjust the size of the legend keys
#     legend.title = element_text(size = 24),  # Adjust the size of the legend title
#     legend.text = element_text(size = 24)# Adjust the size of the legend text
#   )

signature = c('EventRR', 'TotalRR', 'RR_Seasonality', 'Recession_a_Seasonality', 'AverageStorage',
              'RecessionParameters_b', 'RecessionParameters_T0',
              'First_Recession_Slope', 'Mid_Recession_Slope','EventRR_TotalRR_ratio',
              'VariabilityIndex', 'BaseflowRecessionK',
              'BFI', 'BFI_90')
x_max = c(1, 1, 5, 6, 550, 6, 60, 2, 1, 1, 1, 0.5, 1, 1)
sig_limits = data.frame(signature, x_max)

sig_map_plot_list <- list()
for (sig in unique(hyset_sigs_centroid$signature)) {
  
  x_max_df = sig_limits[sig_limits$signature == sig, ]
  upper_limit = x_max_df$x_max
  
  p = ggplot() +
    geom_sf(data = conus, color = "white", fill = "grey") +  # Plot polygon boundaries, color by variable
    geom_sf(data = hyset_sigs_centroid[hyset_sigs_centroid$signature == sig, ],
            aes(fill = prediction), shape = 21, color = "darkgrey", size = 2, alpha = 1) +
    scale_fill_distiller(palette = "Spectral", direction = 1, name = NULL, limits = c(0, upper_limit)) +
    # scale_fill_gradient(low = "red", high = "blue4") +
    ggtitle(sig) +
    theme_void()
    # theme(
    #   plot.title = element_text(size = 30, hjust = 0.5),  # Adjust title size and centering
    #   legend.key.size = unit(2, "lines"),  # Adjust the size of the legend keys
    #   legend.title = element_text(size = 24),  # Adjust the size of the legend title
    #   legend.text = element_text(size = 24)# Adjust the size of the legend text
    # )
  sig_map_plot_list[[sig]] <- p
}
sig_map_final_plot <- plot_grid(plotlist = sig_map_plot_list, ncol = 3)  # Adjust ncol as needed
print(sig_map_final_plot)

# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures_final/predicted_signatures_map.png", width = 14, height = 14, dpi = 300,bg = "white")


#### Performance Plotting; OLD VERSION ####

# # OLD OUTPUTS; from Python scripts (R2 is prob valid, but not variable importance)
# # outputs, with caravan attributes matched to camels attributes
# rf_performance = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_output.csv')
# rf_performance_plus = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_output.csv')
# rf_performance_camels = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_camels_plus_output.csv')
# 
# # looking at outputs from regional random forests (prob need to re-run with same hyperparameters)
# rf_performance_wet = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_wet_output.csv')
# rf_performance_eco = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_eco_eastern_forests_output.csv')
# 
# # looking at outputs from caravan and new predictors, removing those that are correlated > 0.7
# rf_performance_plus_v3 = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_plus_output_v3.csv')
# rf_performance_v3 = read.csv('E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/rf_performance_caravan_output_v3.csv')



rf_performance_r2 = rf_performance_v3 %>% 
  group_by(sig) %>% 
  summarize(cv_r2 = median(cv_r2)) %>% 
  rename(cv_r2_caravan = cv_r2)

# sorting  high to low predictability
rf_performance_r2$sig <- factor(rf_performance_r2$sig, levels = rf_performance_r2$sig[order(rf_performance_r2$cv_r2_caravan, decreasing = TRUE)])


# adding the new attributes
rf_performance_plus_r2 = rf_performance_plus_v3 %>% 
  group_by(sig) %>% 
  summarize(cv_r2 = median(cv_r2)) %>% 
  rename(cv_r2_plus = cv_r2)


# rf_performance_camels_r2 = rf_performance_camels %>% 
#   group_by(sig) %>% 
#   summarize(cv_r2 = median(cv_r2)) %>% 
#   rename(cv_r2_camels = cv_r2)

rf_performance_final =  rf_performance_r2 %>% 
  left_join(rf_performance_plus_r2, by = "sig") %>%
  # left_join(rf_performance_camels, by = "sig") %>% 
  pivot_longer(-sig, names_to = "r2_variable", values_to = "value") %>% 
  arrange(r2_variable) %>% 
  filter(sig != "Spearmans_rho") %>% 
  filter(sig != "MRC_num_segments") %>% 
  filter(sig != "RecessionParameters_a")
  
  

# eventually, want a bar plot with two different R2 for each signature
# R2 when inlcude or remove the new catchment attributes
# to do so, have the data long, with another column labeling R2with and R2without
# then, geom_col(data = df, aes(x = sigs, y = value, fill = r2_variable)

# boxplot, R2 on y axis, signature on x axis
ggplot(rf_performance_final, aes(x = sig, y = value, fill = r2_variable)) +
  geom_col(position = "dodge", width = 0.6) +
  labs(
    y = "Mean R2",
    x = NULL,
    title = NULL
  ) +
  scale_y_continuous(limits = c(0, 1)) +
  theme_minimal()+
  theme(
    plot.title = element_text(size = 24),
    text = element_text(size = 14),   # Increase text (axis labels, title) size
    axis.text.x = element_text(angle = 45, hjust = 1, size = 14),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 16),
    legend.text = element_text(size = 14),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  )+
  scale_fill_manual(name = "RF Model Performance",  # Changing legend name
                      labels = c("Caravan attributes", "Plus new attributes"),
                      values = c("blue", "green"))


# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest/figures_final/rf_performance_r2_v3.png", width = 12, height = 6, dpi = 300,bg = "white")


# trying slightly different aesthetics
ggplot(rf_performance_r2, aes(x = sig, y = cv_r2)) +
  geom_col(width = 0.6) +  # Adjust the width of the bars
  labs(
    y = "R2",
    x = NULL,
    title = "Model Performance, Cross Validation"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 24),
    axis.text.x = element_text(angle = 45, hjust = 1),  
    axis.text.y = element_text(size = 14),
    axis.title = element_text(size = 16),  # Adjust axis title size
    legend.position = "none"  # Remove legend
  )



#### VARIABLE IMPORTANCE PLOTTING (incMSE) ####
rf_performance_test = rf_performance %>% 
  filter(cv_r2 > 0.4) %>% 
  filter(IncMSE > 0)

rf_performance_2 = rf_performance_v3 %>% 
  mutate(IncMSE_Category = case_when(
    IncMSE <= 5 ~ "<5",
    IncMSE > 5 & IncMSE <= 15 ~ "5-15",
    IncMSE > 15 & IncMSE <= 25 ~ "15-25",
    IncMSE > 25 & IncMSE <= 35 ~ "25-35",
    IncMSE > 35 ~ "35+",
  )) %>% 
  mutate(IncMSE_Category = factor(IncMSE_Category, levels = c("<5", "5-15", "15-25", "25-35", "35+")))

# Define the color and size scales
color_scale <- c("grey", "blue", "green", "red", "red")
size_scale <- c(3, 6, 9, 12, 15)

# Define the categories and their corresponding colors and sizes
categories <- c("<5", "5-15", "15-25", "25-35","35+" )

# Create the heatmap plot with categorized colors and sizes
ggplot(rf_performance_2, aes(x = sig, y = variable, color = IncMSE_Category, size = IncMSE_Category)) +
  geom_point() +
  scale_color_manual(values = color_scale, name = "IncMSE") +
  scale_size_manual(values = size_scale) +
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
    title = "Variable Importance"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)

ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest/figures_final/rf_v3_incmse.png", width = 10, height = 8, dpi = 300,bg = "white")



# trying the continuous scale plotting
# I still don't love the color scales since a lot of the data is middle range, but ok for now


rf_variables = rf_performance_eco %>% 
  filter(sig != "Spearmans_rho") %>% 
  filter(sig != "MRC_num_segments") %>% 
  filter(sig != "RecessionParameters_a") %>% 
  mutate(IncMSE = ifelse(IncMSE <0, 0, IncMSE))

rf_variables_2 = rf_performance_plus_v3 %>% 
  filter(sig != "Spearmans_rho") %>% 
  filter(sig != "MRC_num_segments") %>% 
  filter(sig != "RecessionParameters_a") %>% 
  mutate(IncMSE = ifelse(IncMSE <0, 0, IncMSE))

# desired_order <- rev(c("p_mean", "pet_mean", "aridity", "frac_snow","moisture_index", "seasonality", "high_prec_freq", "high_prec_dur",
#                    "low_prec_freq", "low_prec_dur",
#                    "ele_mt_smn", "slp_dg_sav", 'area',
#                    'for_pc_sse',
#                    "swc_pc_syr", "cly_pc_sav", "slt_pc_sav", "snd_pc_sav", "soc_th_sav", "kar_pc_sse",
#                    'fresh_no_giw', 'geol_major_age_ma' ))

# # updated list of attributes
# desired_order <- rev(c("p_mean", "pet_mean", "frac_snow", "seasonality", "high_prec_freq", "high_prec_dur",
#                        "ele_mt_smn", "slp_dg_sav", 'area',
#                        'for_pc_sse',
#                        "cly_pc_sav", "slt_pc_sav", "soc_th_sav", "kar_pc_sse",
#                        'giw_frac', 'geol_av_age_ma' ))
# 
# 
# rf_variables_2$variable <- factor(rf_variables_2$variable, levels = desired_order)
# 
# ggplot(rf_variables_2, aes(x = sig, y = variable, fill = IncMSE, size = IncMSE)) +
#   geom_point(shape = 21, color = 'black') +
#   # scale_color_viridis_c()+
#   scale_fill_gradient2(low = "white",high = "black", name = "IncMSE",
#                         midpoint = median(rf_variables_2$IncMSE),  limits = c(0, 35)) +
#   scale_size_continuous(range = c(2, 8)) +
#   labs(
#     y = NULL,  # No y-axis label
#     x = NULL,
#   ) + # Add plot title
#   theme_minimal() +                    # Use a minimal theme
#   theme(
#     plot.title = element_text(size=24),
#     text = element_text(size = 20),   # Increase text (axis labels, title) size
#     axis.title = element_text(size = 14),  # Increase axis title size
#     axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
#     axis.text.y = element_text(size = 14),  # Adjust y-axis text size
#     legend.position = "left",  # Move legend to the left side
#     legend.title = element_text(size = 20),
#     legend.text = element_text(size = 20),  # Adjust legend text size
#     legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
#   ) +
#   guides(size = FALSE)
# 
# # ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest/figures_final/rf_plus_eco_eastern_incmse.png", width = 10, height = 8, dpi = 300,bg = "white")
# updated list of attributes
desired_order <- rev(c("p_mean", "pet_mean", "frac_snow", "seasonality", "high_prec_freq", "high_prec_dur",
                       "ele_mt_smn", "slp_dg_sav", 'area',
                       'for_pc_sse',
                       "cly_pc_sav", "slt_pc_sav", "soc_th_sav", "kar_pc_sse",
                       'giw_frac', 'geol_av_age_ma' ))


rf_variables_2$variable <- factor(rf_variables_2$variable, levels = desired_order)

ggplot(rf_variables_2, aes(x = sig, y = variable, fill = IncMSE, size = IncMSE)) +
  geom_point(shape = 21, color = 'black') +
  # scale_color_viridis_c()+
  scale_fill_gradient2(low = "white",high = "black", name = "IncMSE",
                        midpoint = median(rf_variables_2$IncMSE),  limits = c(0, 35)) +
  scale_size_continuous(range = c(2, 8)) +
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
  ) + # Add plot title
  theme_minimal() +                    # Use a minimal theme
  theme(
    plot.title = element_text(size=24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.title = element_text(size = 14),  # Increase axis title size
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_text(size = 14),  # Adjust y-axis text size
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)

# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest/figures_final/rf_plus_eco_eastern_incmse.png", width = 10, height = 8, dpi = 300,bg = "white")
