# Full analysis

from signatures.archive.calculate_sigs_camels import *
from signatures.archive.pca import *
import geopandas
import numpy as np

# Author: Anne Holt (@annieholt)
# Date: 2024

# testing functions
# import data
# pi_path = 'C:/Users/holta/Documents/Repositories/baseflow_prediction/signatures/camels_gw_sigs_pi.obj'
pi_path = 'C:/Users/holta/Documents/Repositories/baseflow_prediction/signatures/camels_gw_sigs_pi_v2.obj'
tossh_path = 'C:/Users/holta/Documents/Repositories/TOSSH'

# get data for hydrologic signatures
sigs = get_sig_df(tossh_path, pi_path)
# sigs.to_csv('E:/SDSU_GEOG/Thesis/Data/Signatures/sigs_camels_v2.csv', index=False)
print(sigs)

# look at the number of NAs
nan_count = sigs.isna().sum()
# print(nan_count)
# select final dataframe of signatures:
# drop NA data
# don't use StorageFraction (McMillan 2022 considers unreliable for large samples) or Recession Parameters for now
sigs_2 = sigs[["gauge_id", "gauge_lat", "gauge_lon", "TotalRR", "EventRR", "RR_Seasonality", "AverageStorage",
               "Recession_a_Seasonality", "MRC_num_segments", "First_Recession_Slope", "Mid_Recession_Slope",
               "Spearmans_rho", "EventRR_TotalRR_ratio", "VariabilityIndex", "BFI",
               "BaseflowRecessionK"]].dropna()

sigs_3 = sigs_2[["TotalRR", "EventRR", "RR_Seasonality", "AverageStorage", "Recession_a_Seasonality",
                 "MRC_num_segments", "First_Recession_Slope", "Mid_Recession_Slope", "Spearmans_rho",
                 "EventRR_TotalRR_ratio", "VariabilityIndex", "BFI", "BaseflowRecessionK"]]

pca = run_pca(sigs_3, 'eigen', 0.8, 'dataframe')
# print(pca)
# pca = run_pca(pi_path, tossh_path, 'variance', None, 'model')
# plot_path = "D:/SDSU_GEOG/Thesis/Data/Signatures"
# plot_pca_explained_variance(pca_model=pca, out_path=plot_path)

cluster = create_cluster_labels(sig_df=pca, num_groups=6)
# print(cluster)
# elbow(sig_df=pca, min_clusters=2, max_clusters=15)

cluster_full = clusters_to_loc(sigs_2, cluster)
print(cluster_full)


cluster_gdf = geopandas.GeoDataFrame(cluster_full, geometry=geopandas.points_from_xy(cluster_full.gauge_lon,
                                                                                     cluster_full.gauge_lat))
print(cluster_gdf.head())

cluster_variables = ["TotalRR", "EventRR", "RR_Seasonality", "AverageStorage", "Recession_a_Seasonality",
                     "MRC_num_segments", "First_Recession_Slope", "Mid_Recession_Slope", "Spearmans_rho",
                     "EventRR_TotalRR_ratio", "VariabilityIndex", "BFI", "BaseflowRecessionK"]
cluster_sizes = cluster_gdf.groupby("Cluster").size()
cluster_means = cluster_gdf.groupby("Cluster")[cluster_variables].mean()
cluster_means_2 = cluster_means.T.round(3)
print(cluster_sizes)
print(cluster_means_2)


# now create dataset of 48 contiguous United States
# import from local file
usa = geopandas.read_file('E:/SDSU_GEOG/Thesis/Data/US states/cb_2018_us_state_500k/cb_2018_us_state_500k.shp')
state_names = ["Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut",
               "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Iowa", "Idaho",
               "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine",
               "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota",
               "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
               "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
               "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin",
               "West Virginia", "Wyoming"]
# only retain the 48 states
usa_48 = usa[usa['NAME'].isin(state_names)]
print(usa_48.crs)

# create plot of gauges over state boundaries
# color by BFI
ax = usa_48.plot(color='white', edgecolor='black')

ClusterPalette = {0: 'red', 1: 'green', 2: 'blue', 3: 'orange', 4: 'purple', 5: 'yellow'}

# Loop through each attribute type and plot it using the colors assigned in the dictionary
for ctype, data in cluster_gdf.groupby('Cluster'):
    # Define the color for each group using the dictionary
    color = ClusterPalette[ctype]
    # Plot each group using the color defined above
    data.plot(color=color,
              ax=ax,
              label=ctype)

ax.legend(bbox_to_anchor=(1.0, .5), prop={'size': 12})
# ax.set(title='Catchment Classification based on Baseflow Signatures')
ax.set_axis_off()
plt.show()
# plt.savefig('D:/SDSU_GEOG/Thesis/Data/Signatures/CAMELS_baseflow_clusters.png')


# cluster_gdf.plot(ax=ax, column="Cluster", cmap='Set1', legend=True, legend_kwds={'shrink': 0.4})
# plt.show()