# %%
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import seaborn as sns
import numpy as np
import textwrap

# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################
file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph+padcat.csv"
num_clusters = 6
seed = 0

selected_columns = [
    "PPTAVG_BASIN",
    "T_AVG_BASIN",
    "T_MAXSTD_BASIN",
    "T_MIN_BASIN",
    "T_MINSTD_BASIN",
    "RH_BASIN",
    "FST32F_BASIN",
    "LST32F_BASIN",
    "WD_BASIN",
    "WDMAX_BASIN",
    "WDMIN_BASIN",
    "PET",
    "SNOW_PCT_PRECIP",
    "PRECIP_SEAS_IND",
    "moisture_index",
    "seasonality",
    "high_prec_freq",
    "high_prec_dur",
    "low_prec_freq",
    "low_prec_dur",
    "PETdivP",
    "input_seasonality",
    "input_PET_synchrony",
    "gauge_lat",
    "gauge_lon",
]  # More climate attrs

# selected_columns = [
#     "ELEV_MEAN_M_BASIN",
#     "SLOPE_PCT",
#     "P_mm_day",
#     "PET_mm_day",
#     "ARIDITY_GAGES2",
#     "SNOW_PCT_PRECIP",
#     "PRECIP_SEAS_IND",
#     "high_prec_freq",
#     "low_prec_freq",
#     "low_prec_dur",
#     "gauge_lat",
#     "gauge_lon",
# ]  # Only for claimtes
# selected_columns = [
#     "ELEV_MEAN_M_BASIN",
#     "DRAIN_SQKM",
#     "SLOPE_PCT",
#     "FORESTNLCD06",
#     "CROPSNLCD06",
#     "PASTURENLCD06",
#     "PCT_IRRIG_AG",
#     "SNOWICENLCD06",
#     "PADCAT1_AND_2",
#     "isowet_areafrac",
#     "CLAYAVE",
#     "SILTAVE",
#     "OMAVE",
#     "kar_pc_sse",
#     "geol_weighted_ave_age_ma",
#     "PDEN_2000_BLOCK",
#     "gdp_ud_sav",
#     "FRAGUN_BASIN",
#     "P_mm_day",
#     "PET_mm_day",
#     "ARIDITY_GAGES2",
#     "SNOW_PCT_PRECIP",
#     "PRECIP_SEAS_IND",
#     "high_prec_freq",
#     "low_prec_freq",
#     "low_prec_dur",
#     "ASPECT_NORTHNESS",
#     "ASPECT_EASTNESS",
#     "gauge_lat",
#     "gauge_lon",
# ]  # GAGES2
# file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_caravan_us_epa.csv"
# selected_columns = [
#     "ele_mt_sav",
#     "area",
#     "sgr_dk_sav",
#     "for_pc_sse",
#     "crp_pc_sse",
#     "pst_pc_sse",
#     "ire_pc_sse",
#     "prm_pc_sse",
#     "pac_pc_sse",
#     "isowet_areafrac",
#     "cly_pc_sav",
#     "slt_pc_sav",
#     "soc_th_sav",
#     "kar_pc_sse",
#     "geol_weighted_ave_age_ma",
#     "ppd_pk_sav",
#     "gdp_ud_sav",
#     "hdi_ix_sav",
#     "p_mean",
#     "pet_mean",
#     "aridity",
#     "frac_snow",
#     "seasonality",
#     "high_prec_freq",
#     "low_prec_freq",
#     "low_prec_dur",
#     "gauge_lat",
#     "gauge_lon",
# ]  # For Caravan
# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################

_data = pd.read_csv(file_path)
data = _data[_data["country"] == "United States of America"]
print(len(data))

# %%
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
# %%
# Apply t-SNE (this is going to take a while)
tsne = TSNE(n_components=2, random_state=seed)
data_tsne = tsne.fit_transform(data_scaled)

# %%
# Apply K-Means clustering
kmeans = KMeans(n_clusters=num_clusters, random_state=seed)
clusters = kmeans.fit_predict(data_scaled)
# %% #########################################################################
#
# t-SNE PLOTTING
#
##############################################################################
cmap = "Set2"
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
plt.colorbar(scatter, label="Cluster")
plt.title("t-SNE Clusters on Map")
plt.show()

# %%
for cluster in range(num_clusters):
    # Create a scatter plot on a map
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    ax.set_extent([-125, -66.5, 24, 49], crs=ccrs.PlateCarree())

    # Scatter plot with color based on clusters
    scatter = ax.scatter(
        lat_lon["gauge_lon"][clusters == cluster],
        lat_lon["gauge_lat"][clusters == cluster],
        c=clusters[clusters == cluster],
        s=100,
        alpha=0.1,
        transform=ccrs.PlateCarree(),
    )
    plt.title("Cluster " + str(cluster))
    plt.show()

# %% #########################################################################
#
# BOX PLOTTING
#
##############################################################################

# Selected attributes for box plots
box_attributes = [
    "PPTAVG_BASIN",
    "T_AVG_BASIN",
    "T_MAXSTD_BASIN",
    "RH_BASIN",
    "FST32F_BASIN",
    "LST32F_BASIN",
    "WD_BASIN",
    "PET",
    "SNOW_PCT_PRECIP",
    "PRECIP_SEAS_IND",
    # "peakSWEdivP",
    "PETdivP",
    "input_seasonality",
    "input_PET_synchrony",
]
# box_attributes = [
#     "SLOPE_PCT",
#     "FORESTNLCD06",
#     "CLAYAVE",
#     "geol_weighted_ave_age_ma",
#     "ARIDITY_GAGES2",
#     "SNOW_PCT_PRECIP",
# ]  # For caravan

# box_attributes = [
#     "ELEV_MEAN_M_BASIN",
#     "SLOPE_PCT",
#     "P_mm_day",
#     "PET_mm_day",
#     "ARIDITY_GAGES2",
#     "SNOW_PCT_PRECIP",
#     "PRECIP_SEAS_IND",
#     "high_prec_freq",
#     "low_prec_freq",
#     "low_prec_dur",
# ]  # For climates

# box_attributes = [
#     "sgr_dk_sav",
#     "for_pc_sse",
#     "cly_pc_sav",
#     "geol_weighted_ave_age_ma",
#     "aridity",
#     "frac_snow",
# ]  # For caravan
# %%
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
fig, axes = plt.subplots(3, 3, figsize=(12, 12))

# Define flier properties for outliers
flierprops = dict(marker=".", color="#F2F0EF", alpha=0.1)

for cluster in range(num_clusters):
    row = cluster // 3
    col = cluster % 3

    cluster_data = data_scaled_df[box_attributes][data_scaled_df["cluster"] == cluster]
    plot_cluster_data = cluster_data.melt(var_name="attribute", value_name="value")

    axes[row, col].axhline(0, linestyle="--", color="grey", linewidth=1.0)
    sns.boxplot(
        x="attribute",
        y="value",
        data=plot_cluster_data,
        ax=axes[row, col],
        palette=cmap,
        legend=False,
        flierprops=flierprops,
    )

    axes[row, col].set_title(f"Cluster {cluster}")
    axes[row, col].set_ylabel("Scaled Value")
    axes[row, col].set_ylim([-4, 6])
    # Wrap long x-axis labels
    labels = axes[row, col].get_xticklabels()
    wrapped_labels = [
        "\n".join(textwrap.wrap(label.get_text(), 20)) for label in labels
    ]
    axes[row, col].set_xticklabels(wrapped_labels, rotation=90)
    axes[row, col].set_xlabel(None)

# Hide any unused subplots
plt.tight_layout()
plt.show()

# %%
