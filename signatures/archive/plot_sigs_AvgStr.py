# %%
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
import matplotlib as mpl

import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20250525"
plot_sigs_config_path = "plot_sigs_config.csv"
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

fig_dir = os.path.join(out_dir, "figs")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)
# %%
# ____________________________________________________________________________________
# Load overlay layer for plotting
print("Loading overlay layer...")
_ecoregion_overlay = gpd.read_file(
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\EcoRegions\NA_CEC_Eco_Level2.shp"
)
_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
# %%
# ____________________________________________________________________________________
# Load data
print("Loading attributes data...")

caravan_attrs_dir = r"D:\data\Caravan1.5\attributes"
attrs_camels_file = os.path.join(
    caravan_attrs_dir,
    "camels",
    "attributes_other_camels.csv",
)
attrs_hysets_file = os.path.join(
    caravan_attrs_dir,
    "hysets",
    "attributes_other_hysets.csv",
)
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
attrs_caravan = pd.concat([attrs_camels, attrs_hysets])

eco_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\EcoRegions\Ecoregion_camels.csv"
eco_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\EcoRegions\Ecoregion_hysets.csv"
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])

# %%
print("Loading watershed shapefiles...")
wspolygon_camels_file = r"D:\data\Caravan1.5\shapefiles\camels\camels_basin_shapes.shp"
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = r"D:\data\Caravan1.4\shapefiles\hysets\hysets_basin_shapes.shp"
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets], ignore_index=True)
wspolygon.set_index("gauge_id", inplace=True)

# %% #######################################################
# Loading the data
#######################################################
print("Loading signatures results file ...")
_df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area.csv"),
    index_col="gauge_id",
)
_df_sigs = _df_sigs.drop(
    columns=["area", "country", "gauge_lat", "gauge_lon", "gauge_name"]
)
# _df_sigs = pd.read_csv(
#     os.path.join(out_dir, "out_calc_All_custom"),
#     index_col="gauge_id",
# )

_df_sigs = _df_sigs.join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")

df_sigs = wspolygon.join(df_sigs, how="right")


# %% ######################
# FUNCTIONS
##########################


def plot_sig_map(df, sig_name, overlay_layer, stats="normal", plot_mode="scatter"):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="darkgrey",  # Set land color to light gray
    )
    ax.add_feature(land)

    # Set extent to CONUS
    # ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    # Add map features
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

    # Plotting the filtered data
    if stats == "normal":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name]
        llim = 0
        ulim = 500
        cbar_label = f"{plot_config['unit']}"
        out_file_name = f"map_{sig_name}_{plot_mode}.png"
        title_label = f"{plot_config['label']}"
    elif stats == "percentile":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name + "_perc"]
        llim = 0
        ulim = 100
        cbar_label = "percentile"
        out_file_name = f"map_perc_{sig_name}_{plot_mode}.png"
        title_label = f"{plot_config['label']}"
    elif stats == "process_perc":
        c_data = df[sig_name + "_medperc"]
        llim = 0
        ulim = 100
        cbar_label = "Median percentile"
        out_file_name = f"map_medperc_{sig_name}_{plot_mode}.png"
        title_label = sig_name

    # Create a colormap and normalize
    cmap = plt.cm.Blues
    if "diff_" in sig_name:
        cmap = plt.cm.RdBu_r
    norm = mpl.colors.Normalize(vmin=llim, vmax=ulim)

    if plot_mode == "scatter":
        plot_obj = ax.scatter(
            df["gauge_lon"],
            df["gauge_lat"],
            c=c_data,
            cmap="YlGnBu",
            marker="o",
            # edgecolors="grey",
            s=5,
            # alpha=0.5,
            zorder=99,
            vmin=llim,
            vmax=ulim,
        )
        cbar = plt.colorbar(plot_obj, ax=ax, shrink=0.5)
        cbar.set_label(cbar_label, rotation=270, labelpad=30)
    elif plot_mode == "polygon":
        df_sorted = df.sort_values("area", ascending=False)
        plot_obj = df_sorted.plot(
            ax=ax,
            column=sig_name,
            cmap="YlGnBu",
            alpha=0.7,
            vmin=llim,
            vmax=ulim,
            zorder=99,
        )

        # Add a colorbar
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []  # Empty array for ScalarMappable
        cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label(cbar_label, rotation=270, labelpad=30)

    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    ax.set_title(title_label)

    plt.tight_layout(pad=1.5)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, out_file_name), dpi=300)


# %% ######################
#
#  Plot signature value map
#
##########################

# _____________________________________________________________________________
# Plot signature value map
# For testing
# plot_sig_map(
#     df_sigs, "AverageStorage", ecoregion_overlay, stats="normal", plot_mode="polygon"
# )

plot_sig_map(
    df_sigs, "AverageStorage", ecoregion_overlay, stats="normal", plot_mode="scatter"
)

# %%
Seb_path = (
    r"C:\Users\flipl\dev\TOSSH_signatures_Caravan\results\TOSSH_signatures_Caravan.csv"
)
Seb_sigs = pd.read_csv(Seb_path, index_col="gauge_id")

# Compare the AverageStorage in df_sigs and Seb_sigs
# Plot the scatter plot
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(df_sigs["AverageStorage"], Seb_sigs["AverageStorage"], alpha=0.5)
ax.set_xlabel("AverageStorage in df_sigs")
ax.set_ylabel("AverageStorage in Seb_sigs")
plt.show()

# %%


# %%
