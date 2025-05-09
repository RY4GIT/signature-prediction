# %%
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
    # "#a6d854",
    # "#66c2a5",
    # "#fc8d62",
    # "#e78ac3",
]
cmap = ListedColormap(custom_colors)
# All available climate attrs at BASIN level, annual scale
# From Caravan, GAGES2, and Hammond


"""2025-04-29 Current best

file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph+padcat.csv"
num_clusters = 6
seed = 0

selected_columns = [
    "P_mm_day",
    "T_AVG_BASIN",
    "PET_mm_day",
    "RH_BASIN",
    "ARIDITY_GAGES2",
    "moisture_index",  # ? Sometimes shows different patterns than ARIDITY_GAGES2
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

custom_colors = [
    "#a6d854",
    "#66c2a5",
    "#e78ac3",
    "#8da0cb",
    "#ffd92f",
    "#fc8d62",
]
cmap = ListedColormap(custom_colors)
"""

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

# Option: Apply K-Means clustering
# kmeans = KMeans(n_clusters=num_clusters, random_state=seed)
# clusters = kmeans.fit_predict(data_scaled)

# from sklearn.cluster import MeanShift

# meanshift = MeanShift()
# clusters = meanshift.fit_predict(data_scaled)

# from sklearn.cluster import DBSCAN

# dbscan = DBSCAN(min_samples=100)
# clusters = dbscan.fit_predict(data_scaled)

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
plt.show()

# %% #########################################################################
#
# MAP PLOTTING
#
##############################################################################
# Create a scatter plot on a map
plt.figure(figsize=(10, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.add_feature(cfeature.LAKES, alpha=0.5)
ax.add_feature(cfeature.RIVERS)

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
cbar = plt.colorbar(
    mappable=scatter, ticks=np.arange(np.min(clusters), np.max(clusters) + 1)
)
cbar.set_label("Cluster")
plt.title("t-SNE Clusters on Map")
plt.show()

# %%
# Plot each cluster on a map in a 3-by-2 subplot layout
nrows = 4
fig, axes = plt.subplots(
    nrows, 2, figsize=(15, 4 * nrows), subplot_kw={"projection": ccrs.PlateCarree()}
)
axes = axes.flatten()
for cluster in range(num_clusters):
    # Create a scatter plot on a map
    ax = axes[cluster]
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN, facecolor="lightgrey")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    ax.set_extent([-125, -66.5, 24, 49], crs=ccrs.PlateCarree())

    # Scatter plot with color based on clusters
    scatter = ax.scatter(
        lat_lon["gauge_lon"][clusters == cluster],
        lat_lon["gauge_lat"][clusters == cluster],
        c=custom_colors[cluster],
        s=100,
        alpha=0.7,
        transform=ccrs.PlateCarree(),
    )
    ax.set_title("Cluster " + str(cluster))

# Hide any unused subplots
for i in range(num_clusters, len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()

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
# Create a subplot for each cluster
num_clusters = len(np.unique(clusters))
if num_clusters > 6:
    nrows = 4
else:
    nrows = 3
fig, axes = plt.subplots(3, 2, figsize=(4 * nrows, 12))
axes = axes.flatten()
# Define flier properties for outliers
flierprops = dict(marker=".", color="#F2F0EF", alpha=0.1)


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

    axes[cluster].set_title(f"Cluster {cluster}")
    axes[cluster].set_ylabel("Scaled Value")
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
plt.show()

# %% #########################################################################
#
# SAVE DATA
#
##############################################################################

# Save the data with the cluster labels
data_filtered = data.loc[data_selected_filt.index]
data_filtered["cluster"] = clusters

data_output = data.merge(
    data_filtered[["cluster"]], left_index=True, right_index=True, how="left"
)

cluster_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph+padcat+cluster.csv"
data_output.to_csv(
    cluster_file,
    index=True,
)

# %% Check the number of gauges in each ecoregion
data_output[["CLASS", "AGGECOREGION"]].groupby("AGGECOREGION").count().to_clipboard()
# %% Check the number of gauges in each cluster
data_output[["CLASS", "cluster"]].groupby("cluster").count().to_clipboard()


# %% #########################################################################
#
# POST PROTTING WITH ECOREGIONS
#
##############################################################################

data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
assembled_attrs_dir = os.path.join(data_dir, "derived_attrs", "assembled_RA")
caravan_shp_dir = os.path.join(data_dir, "Caravan1.4", "shapefiles")


# %%
# Load the attribute file with cluster labels
cluster_file = os.path.join(
    assembled_attrs_dir, "attrs_cara_and_gages2+climate+morph+padcat+cluster.csv"
)
data_output = pd.read_csv(cluster_file, index_col="gauge_id")
data_output.head()

# %% Load watershed shapefile
print("Loading watershed shapefiles...")
wspolygon_camels_file = os.path.join(
    caravan_shp_dir, "camels", "camels_basin_shapes.shp"
)
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = os.path.join(
    caravan_shp_dir, "hysets", "hysets_basin_shapes.shp"
)
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets], ignore_index=True)
wspolygon.set_index("gauge_id", inplace=True)

data_output = wspolygon.join(data_output, how="right")
data_output.head()

# %%
# ____________________________________________________________________________________
# Load overlay layer for plotting
print("Loading overlay layer...")
_ecoregion_overlay = gpd.read_file(
    os.path.join(data_dir, "EcoRegions", "NA_CEC_Eco_Level2.shp")
)

_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")

# %%
# %%
for cluster in range(num_clusters):
    # Plot each cluster on a map with watershed polygons and ecoregion overlay
    fig, ax = plt.subplots(
        1, 1, figsize=(12, 6), subplot_kw={"projection": ccrs.PlateCarree()}
    )
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN, facecolor="lightgrey")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")

    ax.set_extent([-125.5, -66.95, 24.396308, 50.5], crs=ccrs.PlateCarree())

    df_sorted = data_output.sort_values("area", ascending=False)
    df_cluster = df_sorted[df_sorted["cluster"] == cluster]
    plot_obj = df_cluster.plot(
        ax=ax,
        color=custom_colors[cluster],
        alpha=0.5,
        zorder=99,
        edgecolor="white",
        linewidth=0.3,
    )
    ecoregion_overlay.plot(
        ax=ax,
        edgecolor="grey",
        facecolor="none",
        linewidth=1.0,
        aspect=1.1,
        zorder=100,
    )

    # Add labels only to ecoregion polygons that overlap with cluster data
    # First do a spatial join to find overlapping ecoregions
    overlapping_regions = gpd.sjoin(
        ecoregion_overlay, df_cluster, how="inner", predicate="intersects"
    )

    # Get unique ecoregion IDs that overlap
    overlapping_ids = overlapping_regions.index.unique()

    # Add labels only to the overlapping ecoregions
    for idx, row in ecoregion_overlay.iterrows():
        if idx in overlapping_ids:
            # Get the centroid of the polygon
            centroid = row.geometry.centroid

            # Get the label text and wrap it
            label_text = row["NA_L2CODE"]
            wrapped_text = "\n".join(
                textwrap.wrap(label_text, width=15)
            )  # Adjust width as needed

            # Add the label at the centroid position
            ax.text(
                centroid.x,
                centroid.y,
                wrapped_text,  # Use wrapped text
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=8,
                fontweight="bold",
                color="grey",
                transform=ccrs.PlateCarree(),
                zorder=101,  # Ensure labels appear above polygons
                bbox=dict(
                    facecolor="white", alpha=0.7, edgecolor="none", pad=1
                ),  # Add background for better readability
            )
    ax.set_title("Cluster " + str(cluster))

    plt.tight_layout()
    plt.savefig(
        os.path.join(
            assembled_attrs_dir,
            "figs",
            "cluster_" + str(cluster) + "_w_ecoregion_num.pdf",
        ),
        dpi=300,
        bbox_inches="tight",
    )


# %%
