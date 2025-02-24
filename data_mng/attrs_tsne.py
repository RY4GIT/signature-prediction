# %%
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %%
# Load the dataset
file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_caravan_us_epa.csv"
_data = pd.read_csv(file_path)
data = _data[_data["country"] == "United States of America"]
print(len(data))
# %%
# Select the required columns
selected_columns = [
    "ele_mt_sav",
    "area",
    "sgr_dk_sav",
    "for_pc_sse",
    "crp_pc_sse",
    "pst_pc_sse",
    "ire_pc_sse",
    "prm_pc_sse",
    "pac_pc_sse",
    "isowet_areafrac",
    "cly_pc_sav",
    "slt_pc_sav",
    "soc_th_sav",
    "kar_pc_sse",
    "geol_weighted_ave_age_ma",
    "ppd_pk_sav",
    "gdp_ud_sav",
    "hdi_ix_sav",
    "p_mean",
    "pet_mean",
    "aridity",
    "frac_snow",
    "seasonality",
    "high_prec_freq",
    "low_prec_freq",
    "low_prec_dur",
    "gauge_lat",
    "gauge_lon",
]

# Extract the selected columns
data_selected = data[selected_columns]
data_selected_filt = data_selected.dropna()
lat_lon = data_selected_filt[["gauge_lat", "gauge_lon"]]
len(data_selected_filt)
len(lat_lon)

data_for_input = data_selected_filt.drop(columns=["gauge_lat", "gauge_lon"])
# %%
# Extract latitude and longitude for later use


# %%
from sklearn.preprocessing import StandardScaler

# Scale the data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_for_input)
# %%
from sklearn.manifold import TSNE

# Apply t-SNE
tsne = TSNE(n_components=2, random_state=42)
data_tsne = tsne.fit_transform(data_scaled)


from sklearn.cluster import KMeans

# Apply K-Means clustering
kmeans = KMeans(n_clusters=9, random_state=42)
clusters = kmeans.fit_predict(data_scaled)
# %%

cmap = "Set2"
# Plot t-SNE components
plt.figure(figsize=(8, 6))
plt.scatter(data_tsne[:, 0], data_tsne[:, 1], c=clusters, cmap=cmap, s=3, alpha=0.5)
plt.colorbar(label="Cluster")
plt.xlabel("t-SNE 1")
plt.ylabel("t-SNE 2")
plt.title("t-SNE Clustering Results")
plt.show()
# %%

# %%
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
