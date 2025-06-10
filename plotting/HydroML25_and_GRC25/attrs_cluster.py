# %% Script to cluster watersheds based on watershed attributes (currently set up to use climate-related attributes) and plot the results

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.mixture import GaussianMixture

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import textwrap

import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################
file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph+padcat.csv"
out_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\docs\202505_HydroML\figs"
num_clusters = 6
seed = 0

selected_columns = [
    "P_mm_day",
    "T_AVG_BASIN",
    # "T_MAX_BASIN", # Maybe redundant pretty similar to T_AVG_BASIN
    # "T_MIN_BASIN", # Maybe redundant pretty similar to T_AVG_BASIN
    "PET_mm_day",
    "RH_BASIN",
    "ARIDITY_GAGES2",
    "moisture_index",  # ? Sometimes shows different patterns than ARIDITY_GAGES2
    # "T_MAXSTD_BASIN", # Redundant, we are not looking at the inter-annual change
    # "T_MINSTD_BASIN", # Redundant, we are not looking at the inter-annual change
    "SNOW_PCT_PRECIP",
    "PRECIP_SEAS_IND",
    "input_seasonality",
    "seasonality",
    "input_PET_synchrony",
    "WD_BASIN",
    "high_prec_freq",
    "high_prec_dur",
    "low_prec_freq",
    "low_prec_dur",
    "FST32F_BASIN",
    "LST32F_BASIN",
    # "WDMAX_BASIN", # Redundant, we are not looking at the inter-annual change
    # "WDMIN_BASIN", # Redundant, we are not looking at the inter-annual change
    # "PETdivP", # Use ARIDITY_GAGES2 instead (used in the main experiment)
    "gauge_lat",
    "gauge_lon",
]

custom_colors = [
    "#a6d854",
    "#66c2a5",
    "#e78ac3",
    "#8da0cb",
    "#ffd92f",
    "#fc8d62",
]
cmap = ListedColormap(custom_colors)


# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################

_data = pd.read_csv(file_path, index_col="gauge_id")
data = _data[_data["country"] == "United States of America"]
print(len(data))

# Extract the selected columns
data_selected = data[selected_columns].astype(float)
data_selected_filt = data_selected.dropna()
len(data_selected_filt)

# Extract latitude and longitude for later use
lat_lon = data_selected_filt[["gauge_lat", "gauge_lon"]]
len(lat_lon)

data_for_input = data_selected_filt.drop(columns=["gauge_lat", "gauge_lon"])

# %% #########################################################################
#
# CLUSTER ATTRIBUTES
#
##############################################################################

# Scale the data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_for_input)

# Apply t-SNE (this is going to take a while)
tsne = TSNE(n_components=2, random_state=seed)
data_tsne = tsne.fit_transform(data_scaled)


gmm = GaussianMixture(n_components=num_clusters, random_state=seed)
clusters = gmm.fit_predict(data_scaled)


# %% #########################################################################
#
# MAP PLOTTING
#
##############################################################################
# Create a scatter plot on a map
plt.figure(figsize=(5, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.LAND, facecolor="white")
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.set_extent([-125.5, -66.95, 24.396308, 47.5])


# Remove outer frame line
for spine in ax.spines.values():
    spine.set_visible(False)

# Scatter plot with color based on clusters
scatter = ax.scatter(
    lat_lon["gauge_lon"],
    lat_lon["gauge_lat"],
    c=clusters,
    cmap=cmap,
    s=3,
    alpha=0.5,
    transform=ccrs.PlateCarree(),
)

plt.savefig(
    os.path.join(out_path, "climate_clusters_map.png"), dpi=300, transparent=True
)


# %%
