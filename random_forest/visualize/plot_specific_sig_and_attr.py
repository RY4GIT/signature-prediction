# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Note: For interactive maps, you'll need to install folium: pip install folium

# %%
sig_name = "BFI"
attr_name = "geol_weighted_ave_age_ma"
cluster_num = 0
exp_date = "20250714"

# %% ###################################################
# Load data
########################################################
gdrive_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
attrs_file = os.path.join(
    gdrive_dir,
    r"data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv",
)
sig_file = os.path.join(
    gdrive_dir,
    r"out\signatures\caravan_us_20250525\out_calc_All_custom_filt_qc_snow_area.csv",
)
model_dir = os.path.join(
    gdrive_dir,
    rf"out\random_forest\output_RAraki_{exp_date}_cluster_{cluster_num}",
)

cluster_info_file = r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize\plot_config_expcolors_clusters.json"
with open(cluster_info_file, "r") as f:
    cluster_info = json.load(f)

attrs_df = pd.read_csv(attrs_file, index_col="gauge_id")
sig_df = pd.read_csv(sig_file, index_col="gauge_id")

df = attrs_df.merge(sig_df, left_index=True, right_index=True)


# %% ######################################################
# Plot the signature and attribute relationship (scatter plot)
###########################################################
def plot_sig_and_attr(df, sig_name, attr_name, cluster_num, cluster_info):
    fig, ax = plt.subplots(figsize=(4, 4))

    kwargs = dict(alpha=0.7, s=3)

    # Global plot
    ax.scatter(df[attr_name], df[sig_name], **kwargs, label="All", color="lightgrey")

    # Subset plot
    df_subset = df[df["cluster"] == cluster_num]
    ax.scatter(
        df_subset[attr_name],
        df_subset[sig_name],
        **kwargs,
        label=f"Cluster {cluster_num} - {cluster_info[str(cluster_num)]['name']}",
        color="tab:blue",
    )

    ax.set_xlabel(attr_name)
    ax.set_ylabel(sig_name)
    ax.legend()
    plt.show()


plot_sig_and_attr(df, sig_name, attr_name, cluster_num, cluster_info)


# %% ######################################################
# Plot the partial dependence plot (needs to be done in R)
###########################################################
NotImplemented


# %% ######################################################
# Plot the values on maps (spatial plot)
###########################################################
def plot_map(df, sig_name, attr_name, cluster_num, cluster_info):
    df = df.copy()
    df_subset = df[df["cluster"] == cluster_num]

    # Get plot config

    # Set up the map
    fig, axs = plt.subplots(
        2, 2, figsize=(15, 15), subplot_kw={"projection": ccrs.PlateCarree()}
    )

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="darkgrey",  # Set land color to light gray
    )

    water = cfeature.NaturalEarthFeature(
        "physical",
        "lakes",
        "50m",
        edgecolor="face",
        facecolor="white",  # Set water color to light blue
    )

    # Plot all 4 subplots using loops
    plot_data = [
        (df, sig_name, "All"),
        (df, attr_name, "All"),
        (df_subset, sig_name, f"Cluster {cluster_num}"),
        (df_subset, attr_name, f"Cluster {cluster_num}"),
    ]

    for i, (data, var, title_suffix) in enumerate(plot_data):
        ax = axs[i // 2, i % 2]

        ax.add_feature(land)
        ax.add_feature(water)

        scatter_kwargs = {
            "cmap": "viridis",
            "marker": "o",
            "s": 10,
            "alpha": 0.5,
            "zorder": 99,
        }

        scatter_obj = ax.scatter(
            data["gauge_lon_x"], data["gauge_lat_x"], c=data[var], **scatter_kwargs
        )
        cbar = plt.colorbar(scatter_obj, ax=ax, shrink=0.3)
        cbar.set_label(var)
        # ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
        ax.set_title(f"{var} - {title_suffix}")

    plt.tight_layout(pad=1.5)
    plt.tight_layout()


plot_map(df, sig_name, attr_name, cluster_num, cluster_info)


# %% ######################################################
# Plot interactive map using folium
###########################################################
def plot_interactive_map(df, sig_name, attr_name, cluster_num, cluster_info):
    import folium
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    df = df.copy()
    df_subset = df[df["cluster"] == cluster_num]

    # Create base map centered on US
    center_lat = df["gauge_lat_x"].mean()
    center_lon = df["gauge_lon_x"].mean()

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=5, tiles="OpenStreetMap"
    )

    # Create feature groups for different layers
    all_sig_group = folium.FeatureGroup(name=f"All - {sig_name}", show=True)
    all_attr_group = folium.FeatureGroup(name=f"All - {attr_name}", show=False)
    cluster_sig_group = folium.FeatureGroup(
        name=f"Cluster {cluster_num} - {sig_name}", show=False
    )
    cluster_attr_group = folium.FeatureGroup(
        name=f"Cluster {cluster_num} - {attr_name}", show=False
    )

    # Function to convert values to hex colors using matplotlib colormap
    def get_color_from_value(value, min_val, max_val, colormap="viridis"):
        if pd.isna(value) or max_val == min_val:
            return "#808080"  # Grey for NaN or constant values

        norm_val = (value - min_val) / (max_val - min_val)
        norm_val = np.clip(norm_val, 0, 1)

        cmap = plt.cm.get_cmap(colormap)
        rgba = cmap(norm_val)
        return mcolors.to_hex(rgba)

    # Add all data points for signature
    sig_min, sig_max = df[sig_name].min(), df[sig_name].max()
    for idx, row in df.iterrows():
        if pd.notna(row["gauge_lat_x"]) and pd.notna(row["gauge_lon_x"]):
            color = get_color_from_value(row[sig_name], sig_min, sig_max)
            folium.CircleMarker(
                location=[row["gauge_lat_x"], row["gauge_lon_x"]],
                radius=4,
                popup=f"<b>Gauge ID:</b> {idx}<br><b>{sig_name}:</b> {row[sig_name]:.4f}",
                tooltip=f"ID: {idx} | {sig_name}: {row[sig_name]:.4f}",
                color="white",
                weight=0.5,
                fillColor=color,
                fill=True,
                fillOpacity=0.8,
            ).add_to(all_sig_group)

    # Add all data points for attribute
    attr_min, attr_max = df[attr_name].min(), df[attr_name].max()
    for idx, row in df.iterrows():
        if pd.notna(row["gauge_lat_x"]) and pd.notna(row["gauge_lon_x"]):
            color = get_color_from_value(row[attr_name], attr_min, attr_max)
            folium.CircleMarker(
                location=[row["gauge_lat_x"], row["gauge_lon_x"]],
                radius=4,
                popup=f"<b>Gauge ID:</b> {idx}<br><b>{attr_name}:</b> {row[attr_name]:.4f}",
                tooltip=f"ID: {idx} | {attr_name}: {row[attr_name]:.4f}",
                color="white",
                weight=0.5,
                fillColor=color,
                fill=True,
                fillOpacity=0.8,
            ).add_to(all_attr_group)

    # Add cluster subset for signature
    sig_min_cluster, sig_max_cluster = (
        df_subset[sig_name].min(),
        df_subset[sig_name].max(),
    )
    for idx, row in df_subset.iterrows():
        if pd.notna(row["gauge_lat_x"]) and pd.notna(row["gauge_lon_x"]):
            color = get_color_from_value(
                row[sig_name], sig_min_cluster, sig_max_cluster
            )
            folium.CircleMarker(
                location=[row["gauge_lat_x"], row["gauge_lon_x"]],
                radius=5,
                popup=f"<b>Gauge ID:</b> {idx}<br><b>{sig_name}:</b> {row[sig_name]:.4f}<br><b>Cluster:</b> {cluster_num} - {cluster_info[str(cluster_num)]['name']}",
                tooltip=f"ID: {idx} | {sig_name}: {row[sig_name]:.4f} | Cluster: {cluster_num}",
                color="white",
                weight=2,
                fillColor=color,
                fill=True,
                fillOpacity=0.9,
            ).add_to(cluster_sig_group)

    # Add cluster subset for attribute
    attr_min_cluster, attr_max_cluster = (
        df_subset[attr_name].min(),
        df_subset[attr_name].max(),
    )
    for idx, row in df_subset.iterrows():
        if pd.notna(row["gauge_lat_x"]) and pd.notna(row["gauge_lon_x"]):
            color = get_color_from_value(
                row[attr_name], attr_min_cluster, attr_max_cluster
            )
            folium.CircleMarker(
                location=[row["gauge_lat_x"], row["gauge_lon_x"]],
                radius=5,
                popup=f"<b>Gauge ID:</b> {idx}<br><b>{attr_name}:</b> {row[attr_name]:.4f}<br><b>Cluster:</b> {cluster_num} - {cluster_info[str(cluster_num)]['name']}",
                tooltip=f"ID: {idx} | {attr_name}: {row[attr_name]:.4f} | Cluster: {cluster_num}",
                color="white",
                weight=2,
                fillColor=color,
                fill=True,
                fillOpacity=0.9,
            ).add_to(cluster_attr_group)

    # Add all groups to map
    all_sig_group.add_to(m)
    all_attr_group.add_to(m)
    cluster_sig_group.add_to(m)
    cluster_attr_group.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m


# Create and display the interactive map
interactive_map = plot_interactive_map(
    df, sig_name, attr_name, cluster_num, cluster_info
)
interactive_map
