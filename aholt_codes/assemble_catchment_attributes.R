# Script to assemble catchment attribute datasets, for random forest modeling primarily
# Datasources: CAMELS, CARAVAN (version 1.4), and new attributes (calculated in separate repository)
# these data have previously been downloaded locally, and are import throughout the script below

# first, CAMELS, CARAVAN, and new attributes are assembled for the 671 CAMELS US catchments
# attributes are also later assembled for the HYSETS catchments (not including CAMELS catchments)

# Author: Anne Holt (@annieholt)
# Date: 2024

library(tidyverse)
library(randomForest)
library(caret)
library(rpart)
library(rpart.plot)
library(sf)


#### Hydrologic Signatures ####

# sigs_c = read.csv('E:/SDSU_GEOG/Thesis/Data/Signatures/sigs_camels_v2.csv', colClasses = c(gauge_id = "character"))
# 
# # choosing a subset, based on recommendations from McMillan et al. 2022
# # (McMillan et al. 2022 found Storage Fraction was not very reliable for large samples; Average Storage more reliable)
# # this dataset also includes BFI90, as recommended by Gnann et al., 2021
# 
# sigs_c_2 = sigs_c %>% 
#   select(gauge_id, TotalRR, RR_Seasonality, EventRR, Recession_a_Seasonality,
#          AverageStorage, RecessionParameters_a, RecessionParameters_b, RecessionParameters_c, MRC_num_segments,
#          First_Recession_Slope, Mid_Recession_Slope, Spearmans_rho, EventRR_TotalRR_ratio,
#          VariabilityIndex, BFI, BFI_90, BaseflowRecessionK) %>% 
#   as.data.frame() %>% 
#   rename(RecessionParameters_T0 = RecessionParameters_c)


#### New Attributes (Wetland area fractions and geologic age) ####

# these results were generated in a separate workflow/repository; just importing the results below

nwi_c = st_read('E:/SDSU_GEOG/Thesis/Data/NWI_outputs/Shapefiles/nwi_camels_metrics_ecoregions.shp') %>% 
  as.data.frame() %>% 
  select(gauge_id, shed_area, fresh, lake, other)
giws = st_read('E:/SDSU_GEOG/Thesis/Data/GIWs/giws_metrics.shp') %>% 
  as.data.frame() %>% 
  select(gauge_id, area_frac)

# age by major geologic unit
geol_c = st_read('E:/SDSU_GEOG/Thesis/Data/Geology_outputs/Shapefiles/sgmc_camels_metrics.shp') %>% 
  as.data.frame() %>% 
  # select(gauge_id, av_age) %>% 
  rename(geol_major_age_ma = av_age) %>% 
  select(gauge_id, major_lith, lith_area_, geol_major_age_ma)
# average age of catchment (age weighted by area of geologic unit type)
geol_c_av = st_read('E:/SDSU_GEOG/Thesis/Data/Geology_outputs/Shapefiles/sgmc_camels_metrics_age_weighted.shp') %>% 
  as.data.frame() %>% 
  # select(gauge_id, av_age_w) %>% 
  rename(geol_av_age_ma = av_age_w) %>% 
  select(gauge_id, geol_av_age_ma)


new_attrib = nwi_c %>% 
  left_join(giws, by = c("gauge_id")) %>% 
  # some places have zero isolated wetlands, so replace NAs with zero since shapefiles weren't returned for those
  mutate(giw_frac = ifelse(is.na(area_frac), 0, area_frac)) %>% 
  mutate(lake = ifelse(is.na(lake), 0, lake)) %>% 
  mutate(fresh = ifelse(is.na(fresh), 0, fresh)) %>% 
  mutate(other = ifelse(is.na(other), 0, other)) %>% 
  # calculating wetland area, not including geographically isolated
  mutate(fresh_no_giw = fresh + lake - giw_frac) %>% 
  # appending geologic ages
  left_join(geol_c, by = c("gauge_id")) %>% 
  left_join(geol_c_av, by = c("gauge_id")) %>% 
  select(gauge_id, giw_frac, fresh_no_giw, geol_av_age_ma, geol_major_age_ma, major_lith, lith_area_) %>% 
  mutate(giw_frac = ifelse(giw_frac <0, 0, giw_frac))
# write.csv(new_attrib ,"E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_new_attribs.csv", row.names = FALSE )


# also including major lithology classifications, separately
new_attrib_lith = geol_c %>% 
  select(gauge_id, major_lith, lith_area_) %>% 
  mutate(lith_sed_carb = ifelse(major_lith == "Sedimentary, carbonate", 1, 0)) %>% 
  mutate(lith_sed_clast = ifelse(major_lith == "Sedimentary, clastic", 1, 0)) %>% 
  mutate(lith_ig_volc = ifelse(major_lith == "Igneous, volcanic", 1, 0))

# also the watersheds assigned to EcoRegions
nwi_ecoregions = st_read('E:/SDSU_GEOG/Thesis/Data/NWI_outputs/Shapefiles/nwi_camels_metrics_ecoregions.shp') %>% 
  as.data.frame() %>% 
  select(gauge_id,NA_L1KEY)

# write.csv(nwi_ecoregions ,"E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_ecoregions.csv", row.names = FALSE )


#### CAMELS attributes ####

camels_path = "E:/SDSU_GEOG/Thesis/Data/CAMELS/camels-20230412T1401Z"

# camels_name = read.table(paste(camels_path, "/camels_name.txt", sep = ""), sep = ";", header = TRUE)
camels_hydro = read.table(paste(camels_path, "/camels_hydro.txt", sep = ""), sep = ";", header = TRUE)

# just area, mean slope, mean elevation
camels_topo = read.table(paste(camels_path, "/camels_topo.txt", sep = ""), sep = ";", header = TRUE)

camels_clim = read.table(paste(camels_path, "/camels_clim.txt", sep = ""), sep = ";", header = TRUE)

# remove second dominant geological class, as many catchments are one major geology
# follwoing Addor et al., 2018
camels_geol = read.table(paste(camels_path, "/camels_geol.txt", sep = ""), sep = ";", header = TRUE)

# remove soil porosity and conductivity, following Addor et al., 2018
# both are highly correlated with sand fraction
camels_soil = read.table(paste(camels_path, "/camels_soil.txt", sep = ""), sep = ";", header = TRUE)

# remove lai_diff and gvf_diff, following Addor et al., 2018
# both are highly correlated with leaf area index maximum
camels_vege = read.table(paste(camels_path, "/camels_vege.txt", sep = ""), sep = ";", header = TRUE)


# join all together, make sure gauge_id has leading zeros
camels_attribs = camels_topo %>% 
  select(-gauge_lat, -gauge_lon, -area_geospa_fabric) %>% 
  left_join(camels_clim, by = "gauge_id") %>% 
  left_join(camels_geol, by = "gauge_id") %>% 
  left_join(camels_soil, by = "gauge_id") %>% 
  left_join(camels_vege, by = "gauge_id") %>% 
  mutate(gauge_id = str_pad(string = as.numeric(gauge_id), width = 8, side = 'left', pad = 0))

# drop leaf area and gvf difference, soil porosity and cond, and second dom geology based on addor et al. 2018
camels_attribs_addor = camels_attribs %>% 
  select(-lai_diff, -gvf_diff, -soil_porosity, -soil_conductivity, -geol_2nd_class, -glim_2nd_class_frac)

camels_attribs_v2 = camels_attribs %>% 
  select(-lai_diff, -gvf_diff, -soil_porosity, -soil_conductivity, -geol_2nd_class, -glim_2nd_class_frac) %>% 
  # removing categorical variables.... when one-hot encoding, these add a lot of dimensionality for minial icrease in R2
  select(-dom_land_cover_frac, -dom_land_cover, -geol_1st_class, -glim_1st_class_frac,
         -high_prec_timing, -low_prec_timing)

camels_final = camels_attribs_v2 %>% 
  select(-water_frac, -organic_frac) %>%
  select(-pet_mean, -p_mean) %>%
  select(-high_prec_freq, -high_prec_dur) %>%
  select(-soil_depth_pelletier) %>%
  select(-lai_max, -gvf_max)


# write.csv(camels_attribs_v2, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_attribs_v2.csv",
#           row.names = FALSE)


#### CARAVAN attributes, CAMELS watersheds ####

camels_caravan = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/camels/attributes_caravan_camels.csv")

camels_caravan_hydroatlas = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/camels/attributes_hydroatlas_camels.csv")

camels_caravan_other = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/camels/attributes_other_camels.csv")

camels_caravan_attribs = camels_caravan_hydroatlas %>% 
  left_join(camels_caravan, by = "gauge_id") %>% 
  left_join(camels_caravan_other %>% select(gauge_id, area), by = "gauge_id") %>% 
  mutate(gauge_id = gsub("^camels_", "", gauge_id))

# write.csv(camels_caravan_attribs, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_caravan_attribs_all.csv",
#           row.names = FALSE)


# now just choosing attributes similar to CAMELS attributes??
# this will help with rf interpretation and comparison to previous studies
# Note: originally tested some random forests on all of them, and only improved predictability by a few percent

# seleted attributes: 
# topography: mean elevation, average terrain slope, average stream gradient
# landcover: forest cover extent (there are also land use classes, but not including for now)
# soils: clay/silt/sand fraction in soils, organic carbon content, karst area, soil water content
# geology: NA (just have lith classes, which are a lot of categories; not including for now)
# climate: all caravan provides (including frac_snow!!)

# previous version:
# select(gauge_id, ele_mt_smn, slp_dg_sav, sgr_dk_sav,
#        for_pc_sse, gla_pc_sse,
#        cly_pc_sav, slt_pc_sav, snd_pc_sav, soc_th_sav, kar_pc_sse, ero_kh_sav) %>% 


camels_caravan_attribs_v2 = camels_caravan_hydroatlas %>% 
  select(gauge_id, ele_mt_smn, slp_dg_sav,
         glc_cl_smj,
         for_pc_sse,
         cly_pc_sav, slt_pc_sav, snd_pc_sav, soc_th_sav, kar_pc_sse,
         lit_cl_smj) %>% 
  # decided to drop lithology and landcover, because assigned numberic rankings and couldn't break down back into categories
  select(-glc_cl_smj, -lit_cl_smj) %>% 
  left_join(camels_caravan, by = "gauge_id") %>% 
  select(-seasonality, -moisture_index) %>% 
  left_join(camels_caravan_other %>% select(gauge_id, area), by = "gauge_id") %>% 
  mutate(gauge_id = gsub("^camels_", "", gauge_id))

# write.csv(camels_caravan_attribs_v2, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_caravan_attribs_v2.csv",
# row.names = FALSE)


#### Correlation analysis (for plotting and final V3 attribute selections) ####

# Spearman correlation, between camels attributes
correlation_test = camels_attribs_v2 %>% 
  select(-water_frac, -organic_frac) %>% 
  select(-p_mean, -pet_mean) %>% 
  select(-high_prec_freq, -high_prec_dur) %>% 
  select(-soil_depth_pelletier) %>% 
  select(-lai_max, -gvf_max) %>% 
  left_join(new_attrib %>% select(gauge_id, giw_frac, geol_av_age_ma), by = "gauge_id")

correlation_camels_attribs = cor(correlation_test %>% select(-gauge_id) %>% drop_na(), method = "spearman")

cor_example <- cor.test(correlation_test$geol_av_age_ma, correlation_test$geol_porostiy, method = "spearman", exact = FALSE)


# based on results above...
# dropped variables if correlation greater than 0.7; also removed root depth due to NA values
camels_attribs_v3 = camels_attribs_v2 %>% 
  # left_join(new_attrib, by = "gauge_id") %>% 
  select(-slope_mean, -aridity, -high_prec_freq, -high_prec_dur, -low_prec_freq, -gvf_max, -lai_max, -root_depth_99,
         -frac_snow, -root_depth_50)
# write.csv(camels_attribs_v3, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_attribs_v3.csv",
# row.names = FALSE)



# Spearman correlation, caravan attributes in camels catchments

# Calculate Spearman correlation matrix
correlation_caravan_attribs <- cor(camels_caravan_attribs_v3 %>% select(-gauge_id), method = "spearman")

# swc_pc_syr moisture_index
camels_caravan_attribs_v3 = camels_caravan_attribs_v2 %>% 
  select(-snd_pc_sav, -aridity, -high_prec_freq, -high_prec_dur, -low_prec_freq)
# write.csv(camels_caravan_attribs_v3, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/camels_caravan_attribs_v3.csv",
# row.names = FALSE)


# testing a plot, not sure if want these in supplemental results or not...

correlation_data <- as.data.frame(correlation_camels_attribs)
correlation_data$row <- rownames(correlation_data)
correlation_data_long <- tidyr::pivot_longer(correlation_data, -row, names_to = "column", values_to = "correlation")

scatterplot <- ggplot(correlation_data_long, aes(x = column, y = row, fill = correlation, size = abs(correlation))) +
  geom_point(shape = 21, alpha = 0.7) +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0, limits = c(-1, 1)) +
  scale_size(range = c(1, 7)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  labs(title = "Attribute Correlations", x = NULL, y = NULL)

print(scatterplot)
# ggsave("E:/SDSU_GEOG/Thesis/Data/RandomForest_R/figures/camels_attributes_correlations.png", width = 10.5, height = 8, dpi = 300,bg = "white")


# hierarchical clustering; this is just experimental for now
hc <- hclust(dist(correlation_camels_attribs))
correlation_matrix_reordered <- correlation_camels_attribs[hc$order, hc$order]
# Define a custom color palette with a larger range
custom_colors <- colorRampPalette(c("blue", "white", "red"))(100)

# Define color breaks from -1 to 1
breaks <- seq(-1, 1, length.out = 101)

# Create the heatmap without a legend
par(mar = c(5, 4, 4, 2) + 0.1) # Adjust margins if necessary
heatmap(correlation_matrix_reordered,
        Rowv = as.dendrogram(hc),
        Colv = as.dendrogram(hc),
        col = custom_colors,
        breaks = breaks,
        scale = "none",
        margins = c(10, 10),
        main = NULL)



#### New attributes and CARAVAN attributes, Hysets watersheds ####

# Wetland attributes
nwi_hysets = st_read('E:/SDSU_GEOG/Thesis/Data/NWI_hysets/nwi_hysets_metrics.shp') %>% 
  select(gauge_id, shed_area, fresh, lake, other, geometry)

giws_hysets = st_read('E:/SDSU_GEOG/Thesis/Data/GIWs/GIWs_hysets/giws_metrics_hysets.shp') %>% 
  as.data.frame() %>% 
  select(gauge_id, area_frac)

nwi_metrics_hysets = nwi_hysets %>% 
  left_join(giws_hysets, by = "gauge_id") %>% 
  mutate(area_frac = ifelse(is.na(area_frac), 0, area_frac)) %>% 
  mutate(lake = ifelse(is.na(lake), 0, lake)) %>% 
  mutate(fresh = ifelse(is.na(fresh), 0, fresh)) %>% 
  mutate(other = ifelse(is.na(other), 0, other)) %>% 
  mutate(fresh_no_giw = fresh + lake - area_frac)

geol_hysets = st_read('E:/SDSU_GEOG/Thesis/Data/Geology_outputs/Hysets/sgmc_hysets_metrics_age_weighted.shp')
geol_hysets_lith = st_read('E:/SDSU_GEOG/Thesis/Data/Geology_outputs/Hysets/sgmc_hysets_metrics_age_majorlith.shp')

geol_all = geol_c %>%
  bind_rows(geol_hysets)

hysets_caravan = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/hysets/attributes_caravan_hysets.csv")
hysets_caravan_hydroatlas = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/hysets/attributes_hydroatlas_hysets.csv")
hysets_caravan_other = read_csv("E:/SDSU_GEOG/Thesis/Data/Caravan_1.4/attributes/hysets/attributes_other_hysets.csv")


hysets_caravan_attribs_v2 = hysets_caravan_hydroatlas %>% 
  select(gauge_id, ele_mt_smn, slp_dg_sav,
         for_pc_sse,
         cly_pc_sav, slt_pc_sav, snd_pc_sav, kar_pc_sse) %>% 
  left_join(hysets_caravan, by = "gauge_id") %>% 
  left_join(hysets_caravan_other %>% select(gauge_id, area), by = "gauge_id") %>% 
  mutate(gauge_id = gsub("^hysets_", "", gauge_id)) %>% 
  select(-seasonality, -moisture_index)

# joining new attribute data alongside caravan attribute dataset... MAY UPDATE LATER?
# though there are many hyets, just retain ones in the CONUS where I have also calculated new metrics
hysets_caravan_new = nwi_metrics_hysets %>% 
  as.data.frame() %>% 
  select(gauge_id, area_frac) %>% 
  rename(giw_frac = area_frac) %>% 
  left_join(geol_hysets %>% as.data.frame() %>% select(gauge_id, av_age_w), by = "gauge_id") %>% 
  rename(geol_av_age_ma = av_age_w) %>% 
  left_join(hysets_caravan_attribs_v2, by = "gauge_id") %>% 
  drop_na()
  
# write.csv(hysets_caravan_new, "E:/SDSU_GEOG/Thesis/Data/RandomForest_R/inputs/hysets_caravan_attribs_v2.csv",
#           row.names = FALSE)

#### new attribute/caravan attribute correlations, for more specific plots ####

## wetland/signature correlations
corr_attrib_iso = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  as.data.frame() %>% 
  select(-fresh_no_giw, -geol_major_age_ma, -geol_av_age_ma) %>% 
  correlate(method = "spearman") %>% 
  focus(giw_frac) %>% 
  mutate(term_2 = factor(term, levels = term[order(giw_frac)]))

corr_attrib_con = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  as.data.frame() %>% 
  select(-geol_major_age_ma, -giw_frac, -geol_av_age_ma) %>% 
  correlate(method = "spearman") %>% 
  focus(fresh_no_giw) %>% 
  mutate(term_2 = factor(term, levels = term[order(fresh_no_giw)]))

# prep for panel plotting
corr_attrib_wet = corr_attrib_iso %>% 
  left_join(corr_attrib_con) %>% 
  select(term, giw_frac, fresh_no_giw) %>% 
  gather(key = "variable", value = "value", giw_frac, fresh_no_giw)


desired_order <- c("p_mean", "pet_mean", "aridity", "frac_snow","moisture_index", "seasonality", "high_prec_freq", "high_prec_dur",
                       "low_prec_freq", "low_prec_dur",
                       "ele_mt_smn", "slp_dg_sav", 'area',
                       'for_pc_sse',
                       "swc_pc_syr", "cly_pc_sav", "slt_pc_sav", "snd_pc_sav", "soc_th_sav", "kar_pc_sse")

corr_attrib_wet$term <- factor(corr_attrib_wet$term, levels = desired_order)

# Define custom labels for facet_wrap
wet_labels <- c(
  "fresh_no_giw" = "Connected Wetlands",
  "giw_frac" = "Isolated Wetlands"
)

ggplot(corr_attrib_wet, aes(x = term, y = 1, color = value, size = abs(value))) +
  geom_point() +
  scale_color_gradient2(low = "blue", mid = "grey", high = "red", 
                        midpoint = mean(corr_attrib_wet$value), name = "Spearman's Rho",
                        limits = c(-1, 1)) +
  scale_size(range = c(2, 12)) +  # Adjust the overall size scale
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
  ) +
  # ggtitle("Correlations with Isolated Wetland Area Fraction") +
  theme_minimal() +                    # Use a minimal theme
  theme(
    plot.title = element_text(size=24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.title = element_text(size = 14),  # Increase axis title sizehttp://127.0.0.1:42413/graphics/plot_zoom_png?width=619&height=258
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_blank(),  # Remove y-axis values
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)+
  # coord_cartesian(ylim = c(1, 1))
  facet_wrap(~ variable, scales = "free_y", nrow = 2, labeller = as_labeller(wet_labels))

ggsave("E:/SDSU_GEOG/Thesis/Data/Signatures/figures_final/attributes_wetlands_correlations.png", width = 10.5, height = 6, dpi = 300,bg = "white")


# geology 

corr_attrib_geol = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  as.data.frame() %>% 
  select(-fresh_no_giw, -giw_frac, -geol_major_age_ma) %>% 
  correlate(method = "spearman") %>% 
  focus(geol_av_age_ma) %>% 
  mutate(term_2 = factor(term, levels = term[order(geol_av_age_ma)]))

corr_attrib_geol_lith = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  as.data.frame() %>% 
  select(-fresh_no_giw, -giw_frac, -geol_av_age_ma) %>% 
  correlate(method = "spearman") %>% 
  focus(geol_major_age_ma) %>% 
  mutate(term_2 = factor(term, levels = term[order(geol_major_age_ma)]))

# prep for panel plotting
corr_attrib_geol = corr_attrib_geol %>% 
  left_join(corr_attrib_geol_lith) %>% 
  select(term, geol_av_age_ma, geol_major_age_ma) %>% 
  gather(key = "variable", value = "value", geol_av_age_ma, geol_major_age_ma)


corr_attrib_geol$term <- factor(corr_attrib_geol$term, levels = desired_order)

# Define custom labels for facet_wrap
geol_labels <- c(
  "geol_av_age_ma" = "Average Geologic Age",
  "geol_major_age_ma" = "Geoloic Age of Major Lithology"
)

ggplot(corr_attrib_geol, aes(x = term, y = 1, color = value, size = abs(value))) +
  geom_point() +
  scale_color_gradient2(low = "blue", mid = "grey", high = "red", 
                        midpoint = mean(corr_attrib_geol$value), name = "Spearman's Rho",
                        limits = c(-1, 1)) +
  scale_size(range = c(2, 12)) +  # Adjust the overall size scale
  labs(
    y = NULL,  # No y-axis label
    x = NULL,
  ) +
  # ggtitle("Correlations with Isolated Wetland Area Fraction") +
  theme_minimal() +                    # Use a minimal theme
  theme(
    plot.title = element_text(size=24),
    text = element_text(size = 20),   # Increase text (axis labels, title) size
    axis.title = element_text(size = 14),  # Increase axis title sizehttp://127.0.0.1:42413/graphics/plot_zoom_png?width=619&height=258
    axis.text.x = element_text(angle = 45, hjust = 1),  # Rotate x-axis labels diagonally
    axis.text.y = element_blank(),  # Remove y-axis values
    legend.position = "left",  # Move legend to the left side
    legend.title = element_text(size = 20),
    legend.text = element_text(size = 20),  # Adjust legend text size
    legend.key.size = unit(2, "lines")  # Adjust the size of the legend color key
  ) +
  guides(size = FALSE)+
  # coord_cartesian(ylim = c(1, 1))
  facet_wrap(~ variable, scales = "free_y", nrow = 2, labeller = as_labeller(geol_labels))

# ggsave("E:/SDSU_GEOG/Thesis/Data/Signatures/figures_final/attributes_geologic_age_correlations.png", width = 10.5, height = 6, dpi = 300,bg = "white")







#### SCRATCH WORK; mostly testing random forest functions/workflows and catchment datasets ####




### data for practicing RF modeling 
rf_df_final = sigs_c_2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  left_join(camels_attribs, by = "gauge_id")
# write.csv(rf_df_final, "E:/SDSU_GEOG/Thesis/Data/RandomForest/sigs_attributes_master.csv", row.names = FALSE)


rf_caravan_final = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  left_join(sigs_c_2, by = "gauge_id")
# write.csv(rf_caravan_final, "E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_caravan_master_v2_wet.csv", row.names = FALSE)

rf_caravan_final_eco = camels_caravan_attribs_v2 %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  left_join(sigs_c_2, by = "gauge_id") %>% 
  left_join(nwi_ecoregions, by = "gauge_id") %>% 
  # these have the most camels catchments
  filter(NA_L1KEY %in% c("8  EASTERN TEMPERATE FORESTS", "6  NORTHWESTERN FORESTED MOUNTAINS",
                         "9  GREAT PLAINS")) %>% 
  # try just for one first
  filter(NA_L1KEY == "8  EASTERN TEMPERATE FORESTS") %>% 
  select(-NA_L1KEY)
# write.csv(rf_caravan_final_eco, "E:/SDSU_GEOG/Thesis/Data/RandomForest/outputs/sigs_attributes_caravan_master_v2_eco_eastern_forests.csv", row.names = FALSE)


rf_df_1 = camels_hydro %>% 
  select(gauge_id, baseflow_index) %>% 
  left_join(camels_attribs, by = "gauge_id")
# drop_na() %>% 
# select(-gauge_id) %>% 
# select(-low_prec_timing, -high_prec_timing, -geol_1st_class, -glim_1st_class_frac, -dom_land_cover, -dom_land_cover_frac)

# write.csv(rf_df_1, "E:/SDSU_GEOG/Thesis/Data/RandomForest/BFI_attributes_test_data.csv")

rf_df = camels_hydro %>% 
  select(gauge_id, baseflow_index) %>% 
  left_join(camels_attribs, by = "gauge_id") %>% 
  drop_na() %>%
  select(-gauge_id) %>% 
  select(-low_prec_timing, -high_prec_timing, -geol_1st_class, -glim_1st_class_frac, -dom_land_cover, -dom_land_cover_frac)
# select(-dom_land_cover, -geol_1st_class)


# RF AND PERMUTATION; just testing here

# X <- rf_df %>% select(-baseflow_index)
# y <- as.factor(rf_df$baseflow_index)
# 
# # Set seed for reproducibility
# set.seed(42)
# 
# # Split the data into training and test sets
# set.seed(42)  
# indices <- sample(1:nrow(X), size = 0.75 * nrow(X))
# X_train <- X[indices, ]
# X_test <- X[-indices, ]
# 
# # Convert y to character, subset, and convert back to factor
# y_char <- as.character(y)
# y_train <- as.factor(y_char[indices])
# y_test <- as.factor(y_char[-indices])
# 
# # Create and train the Random Forest classifier
# clf <- randomForest(x = X_train, y = y_train, ntree = 100, seed = 42)
# 
# # Predict on the test set
# predictions <- predict(clf, newdata = X_test)
# 
# # Create a confusion matrix
# conf_matrix <- confusionMatrix(predictions, y_test)
# 
# # Calculate accuracy on the test data
# accuracy <- conf_matrix$overall["Accuracy"]
# 
# # Print the accuracy on the test data
# print(paste("Baseline accuracy on test data:", round(accuracy, 2)))


# TESTING AGAIN; this seems like the method moving forward #

## Set seed for reproducibility
set.seed(42)

rf_caravan = camels_caravan_attribs_new %>% 
  left_join(sigs_c_2 %>% select(gauge_id, BFI), by = 'gauge_id') %>% 
  left_join(new_attrib_lith, by = "gauge_id") %>%
  select(-gauge_id) %>% 
  select(-fresh_no_giw, -geol_major_age_ma) %>% 
  select(-major_lith, -lith_area_, -lith_sed_clast, -lith_sed_carb, -lith_ig_volc)

rf_caravan = camels_caravan_attribs %>% 
  left_join(sigs_c_2 %>% select(gauge_id, BFI), by = 'gauge_id') %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  select(-fresh_no_giw, -geol_major_age_ma) %>% 
  select(-gauge_id)

rf_camels = camels_attribs %>% 
  select(-lai_diff, -gvf_diff, -soil_porosity, -soil_conductivity, -geol_2nd_class, -glim_2nd_class_frac) %>%
  select(-dom_land_cover_frac, -dom_land_cover, -geol_1st_class, -glim_1st_class_frac, -high_prec_timing, -low_prec_timing) %>% 
  left_join(sigs_c_2 %>% select(gauge_id, BFI), by = 'gauge_id') %>% 
  left_join(new_attrib, by = "gauge_id") %>% 
  # left_join(new_attrib_lith, by = "gauge_id") %>% 
  select(-fresh_no_giw, -geol_major_age_ma) %>%
  # select(-geol_1st_class, -glim_1st_class_frac, -lith_area_) %>% 
  select(-gauge_id) %>% 
  drop_na()
  # select(geol_1st_class, glim_1st_class_frac, major_lith, lith_area_)

## Define repeated cross-validation with 10 folds and three repeats
# repeat_cv <- trainControl(method = 'repeatedcv', number = 10, repeats = 3, search = 'grid',
#                           allowParallel = TRUE)

repeat_cv <- trainControl(method = 'repeatedcv', number = 10, repeats = 3)

hyper_grid <- expand.grid(
  mtry = c(1:16)  # Adjust the range of mtry values to test
)

# random forest default is number of variables dividied by 3

  ## Train a random forest model using cross-validation
forest <- train(
  # Formula: Predict baseflow_index using all other variables
  BFI ~ .,
  # Source of data
  data = rf_camels,
  # Random forest method
  method = 'rf',
  # Add repeated cross-validation as trControl
  # Metric to evaluate model performance
  
  metric = 'Rsquared',
  # metric = 'RMSE',
  # Number of trees
  trControl = repeat_cv,
  ntree = 500,
  
  # tuneGrid = hyper_grid,
  
  importance = TRUE
)

## Extract the trained random forest model
rf_model_4 <- forest$finalModel
print(forest)
plot(forest)


# var_importance = as.data.frame(rf_model[["importance"]])

# mse for regression
## scale... for permutation, the measures are divided by their standard errors??
var_importance_4 = importance(rf_model_4, type = 1,scale = TRUE)
var_importance_4_df = as.data.frame(var_importance_4)




# CROSS-FOLD VALIDATION/variable importance testing #

## Set seed for reproducibility
set.seed(42)

## Define repeated cross validation with 5 folds and three repeats
repeat_cv <- trainControl(method='repeatedcv', number=10, repeats=3)

## Split the data so that we use 70% of it for training
# train_index <- createDataPartition(y=iris$Species, p=0.7, list=FALSE)
train_index <- createDataPartition(y=rf_df$baseflow_index, p=0.7, list=FALSE)

## Subset the data
training_set <- rf_df[train_index, ]
testing_set <- rf_df[-train_index, ]

## Train a random forest model
forest <- train(
  
  # Formula. We are using all variables to predict Species
  baseflow_index~., 
  
  # Source of data; remove the Species variable
  data=training_set, 
  
  # `rf` method for random forest
  method='rf', 
  
  # Add repeated cross validation as trControl
  trControl=repeat_cv,
  
  # Accuracy to measure the performance of the model
  metric='MAE')

## Print out the details about the model
forest$finalModel



## Get variable importance, and turn into a data frame
var_imp <- varImp(forest, scale=FALSE)$importance
var_imp <- data.frame(variables=row.names(var_imp), importance=var_imp$Overall)

## Create a plot of variable importance
var_imp %>%
  
  ## Sort the data by importance
  arrange(importance) %>%
  
  ## Create a ggplot object for aesthetic
  ggplot(aes(x=reorder(variables, importance), y=importance)) + 
  
  ## Plot the bar graph
  geom_bar(stat='identity') + 
  
  ## Flip the graph to make a horizontal bar plot
  coord_flip() + 
  
  ## Add x-axis label
  xlab('Variables') +
  
  ## Add a title
  labs(title='Random forest variable importance') + 
  
  ## Some layout for the plot
  theme_minimal() + 
  theme(axis.text = element_text(size = 10), 
        axis.title = element_text(size = 15), 
        plot.title = element_text(size = 20), 
  )

# ## Generate predictions
# y_hats <- predict(
#   
#   ## Random forest object
#   object=forest, 
#   
#   ## Data to use for predictions; remove the Species
#   newdata=testing_set[, -1])
# 
# 
# ## Print the accuracy
# accuracy <- mean(y_hats == testing_set$baseflow_index)*100
# cat('Accuracy on testing data: ', round(accuracy, 2), '%',  sep='')


# %%