# %% Script to cluster watersheds based on watershed attributes (currently set up to use climate-related attributes) and plot the results

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.mixture import GaussianMixture

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import textwrap

import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import json


# %% #########################################################################
#
# CONFIGURATION
#
##############################################################################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
file_path = os.path.join(
    cloud_dir,
    "data",
    "derived_attrs",
    "assembled_RA",
    "attrs_cara1p4_gages2_etc_20250311.csv",
)
out_path = os.path.join(cloud_dir, "figs", "subfig_climate_clusters")
if not os.path.exists(out_path):
    os.makedirs(out_path)
cluster_info = json.load(
    open(
        r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\plot_config_expcolors_clusters.json"
    )
)

num_clusters = 6
seed = 0
# All available climate attrs at BASIN level, annual scale
# From Caravan, GAGES2, and Hammond
selected_columns = [
    "P_mm_day",
    "T_AVG_BASIN",
    "PET_mm_day",
    "RH_BASIN",
    "ARIDITY_GAGES2",
    "moisture_index",
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
    "gauge_lat",
    "gauge_lon",
]
# "WDMAX_BASIN", # Redundant, we are not looking at the inter-annual change
# "WDMIN_BASIN", # Redundant, we are not looking at the inter-annual change
# "PETdivP", # Use ARIDITY_GAGES2 instead (used in the main experiment)
# "T_MAXSTD_BASIN", # Redundant, we are not looking at the inter-annual change
# "T_MINSTD_BASIN", # Redundant, we are not looking at the inter-annual change
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
# t-SNE PLOTTING
#
##############################################################################

# Plot t-SNE components
plt.figure(figsize=(8, 6))
plt.scatter(data_tsne[:, 0], data_tsne[:, 1], c=clusters, cmap=cmap, s=3, alpha=0.5)
plt.colorbar(label="Cluster")
plt.xlabel("t-SNE 1")
plt.ylabel("t-SNE 2")
plt.title("t-SNE Clustering Results")
plt.close()

# %% #########################################################################
#
# MAP PLOTTING
#
##############################################################################
# Create a scatter plot on a map

# Set up the map
fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

# Add the BORDERS feature first
ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="k")

# Add the land feature with edgecolor set to black
land = cfeature.NaturalEarthFeature(
    "physical",
    "land",
    "50m",
)
ax.add_feature(
    land,
    facecolor="#F4F5FA",  # Keep facecolor as desired
    edgecolor="black",  # Set edgecolor to black
    linewidth=1.0,  # Optionally adjust linewidth for edges
)
ax.add_feature(cfeature.LAKES, alpha=0.5)

# Scatter plot with color based on clusters
scatter = ax.scatter(
    lat_lon["gauge_lon"],
    lat_lon["gauge_lat"],
    c=clusters,
    cmap=cmap,
    s=5,
    alpha=0.5,
    transform=ccrs.PlateCarree(),
    zorder=99,
)
cbar = plt.colorbar(
    mappable=scatter,
    ticks=np.arange(np.min(clusters), np.max(clusters) + 1),
    shrink=0.3,
)
cbar.set_label("Cluster number")
# plt.title("t-SNE clusters on map")

ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
for spine in ax.spines.values():
    spine.set_visible(False)
plt.tight_layout()
plt.savefig(
    os.path.join(out_path, "fig_climate_clusters.png"),
    dpi=300,
    transparent=True,
    bbox_inches="tight",
)
plt.close()

# %% #########################################################################
#
# BOX PLOTTING
#
##############################################################################

# Selected attributes for box plots
box_attributes = selected_columns[:-2]  # Exclude lat/lon

data_scaled_df = pd.DataFrame(
    np.concatenate(
        (
            data_scaled,
            lat_lon["gauge_lat"].values.reshape(-1, 1),
            lat_lon["gauge_lon"].values.reshape(-1, 1),
        ),
        axis=1,
    ),
    columns=selected_columns,
)
data_scaled_df["cluster"] = clusters
data_scaled_df


# %%


def custom_palette(data):
    colors = []
    for attribute in data["attribute"].unique():
        values = data[data["attribute"] == attribute]["value"]
        q25, q50, q75 = np.percentile(values, [25, 50, 75])
        if q75 < 0:
            colors.append("tab:pink")
        elif q25 > 0:
            colors.append("tab:blue")
        else:
            colors.append("lightgrey")
    return colors


# Create a subplot for each cluster
num_clusters = len(np.unique(clusters))
fig, axes = plt.subplots(3, 2, figsize=(12, 11))
axes = axes.flatten()
# Define flier properties for outliers
flierprops = dict(marker=".", color="#F2F0EF", alpha=0.1)
plt.rcParams.update({"font.size": 12})
for cluster in range(num_clusters):
    row = cluster // 2
    col = cluster % 2

    cluster_data = data_scaled_df[box_attributes][data_scaled_df["cluster"] == cluster]
    plot_cluster_data = cluster_data.melt(var_name="attribute", value_name="value")

    colors = custom_palette(plot_cluster_data)

    axes[cluster].axhline(0, linestyle="--", color="grey", linewidth=1.0)
    sns.boxplot(
        x="attribute",
        y="value",
        data=plot_cluster_data,
        ax=axes[cluster],
        palette=colors,  # cmap
        legend=False,
        flierprops=flierprops,
    )

    axes[cluster].set_title(
        f"Cluster {cluster} - {cluster_info[str(cluster)]['name']} ({len(cluster_data)} gauges)"
    )
    axes[cluster].set_ylabel("Scaled (Standardized)")
    axes[cluster].set_ylim([-5, 5])
    # Wrap long x-axis labels
    labels = axes[cluster].get_xticklabels()
    wrapped_labels = [
        "\n".join(textwrap.wrap(label.get_text(), 20)) for label in labels
    ]
    axes[cluster].set_xticklabels(wrapped_labels, rotation=90)
    axes[cluster].set_xlabel(None)

# Hide any unused subplots
plt.tight_layout()
plt.savefig(
    os.path.join(out_path, "fig_climate_clusters_chars.png"),
    dpi=300,
    transparent=True,
    bbox_inches="tight",
)
print(f"Figures saved in {out_path}")

# %%
