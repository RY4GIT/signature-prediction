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
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")

# Google Drive directory
gdrive_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"

# Local directory (For Caravan data)
local_dir = r"D:\data"

# Output directory (For signatures results, change name to match the current run dates)
out_dir = os.path.join(gdrive_dir, "out", "signatures", "caravan_camels_20250724")

# %%
# ____________________________________________________________________________________
# Load data
print("Loading attributes data...")

caravan_attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
attrs_camels_file = os.path.join(
    caravan_attrs_dir,
    "camels",
    "attributes_other_camels.csv",
)
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")

# %% #######################################################
# Loading the data
############################################################
print("Loading signatures results file ...")
_df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom.csv"),
    index_col="gauge_id",
)
df_sigs = _df_sigs.join(attrs_camels, how="left")

df_sigs["diff_R_Pint_RC"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
# %%
# ____________________________________________________________________________________
# Plotting
############################################################
from matplotlib.colors import LinearSegmentedColormap

# Plot R_Pint_RC and R_Pvol_RC and diff
for sig in ["R_Pint_RC", "R_Pvol_RC", "diff_R_Pint_RC"]:
    # Create figure with CONUS projection
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Set extent for CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.OCEAN, color="lightblue", alpha=0.3)
    ax.add_feature(cfeature.LAND, color="lightgray", alpha=0.1)

    if sig == "diff_R_Pint_RC":
        diagonal_colors = [
            "#159DD0",
            # "#2CA6D4",
            # "#43B0D9",
            "#aeb5b1",
            # "#E38753",
            # "#E0783E",
            "#DD6A29",
        ]

        # Create the colormap
        diag_cmap = LinearSegmentedColormap.from_list(
            "custom_diag_gradient", diagonal_colors
        )

        cmap = diag_cmap
        norm = mpl.colors.Normalize(vmin=-0.1, vmax=0.1)
    else:
        cmap = "viridis"
        norm = mpl.colors.Normalize(vmin=-1, vmax=1)

    # Plot the signature data
    scatter = ax.scatter(
        df_sigs["gauge_lon"],
        df_sigs["gauge_lat"],
        c=df_sigs[sig],
        cmap=cmap,
        norm=norm,
        s=40,  # point size
        alpha=0.7,
        transform=ccrs.PlateCarree(),  # specify that lat/lon are in PlateCarree
    )

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, pad=0.01)
    cbar.set_label(sig, fontsize=12)

    # Add gridlines
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()

    plt.title(f"{sig} - CONUS Distribution", fontsize=16, pad=20)
    plt.tight_layout()
    plt.show()

# %%
