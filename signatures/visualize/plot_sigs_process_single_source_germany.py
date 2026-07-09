# %% Plot signatures from a single source (Caravan)
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
import pyproj

# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")

# Current directory
os.chdir(r"Y:\Gruppen\cathyd\mcmillan\signatures_processes\signature-prediction\signatures\visualize")

# Google Drive directory
gdrive_dir = r"Y:\Gruppen\cathyd\mcmillan\signatures_processes\signature-prediction\Results"

#ArcGis directory
arcgis_dir = r"Y:\Gruppen\cathyd\mcmillan\ArcGis"

# Local directory (For Caravan data)
local_dir = r"D:\data"

# Output directory (For signatures results, change name to match the current run dates)
out_dir = os.path.join(gdrive_dir, "out", "signatures", "caravan_camels_20260707")

# Plotting config
plot_sigs_config_path = "plot_sigs_config.csv"
plot_sigs_config = pd.read_csv(plot_sigs_config_path)
print(plot_sigs_config)

# Figure directory
fig_dir = os.path.join(out_dir, "figs")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


# %%
# ____________________________________________________________________________________
# Load overlay layer for plotting
print("Loading overlay layer...")
_ecoregion_overlay = gpd.read_file(
    os.path.join(arcgis_dir, "DEU_states", "DEU_states.shp")
)
_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
# %%
# ____________________________________________________________________________________
# Load data
# print("Loading attributes data...")
#
# caravan_attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
# attrs_camels_file = os.path.join(
#     caravan_attrs_dir,
#     "camels",
#     "attributes_other_camels.csv",
# )
# attrs_hysets_file = os.path.join(
#     caravan_attrs_dir,
#     "hysets",
#     "attributes_other_hysets.csv",
# )
# attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
# attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
# attrs_caravan = pd.concat([attrs_camels, attrs_hysets])
#
# eco_camels_file = os.path.join(
#     gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_camels.csv"
# )
# eco_hysets_file = os.path.join(
#     gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_hysets.csv"
# )
# eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
# eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
# eco_caravan = pd.concat([eco_camels, eco_hysets])



# %%
print("Loading watershed shapefiles...")
# File from Larisa's set of catchments
wspolygon_rr2_file = os.path.join(
    arcgis_dir, "catchments_RR2", "catchments_RR2.shp"
)
wspolygon = gpd.read_file(wspolygon_rr2_file).to_crs(epsg=4326)
# wspolygon_hysets_file = os.path.join(
#     local_dir, "Caravan1.4", "shapefiles", "hysets", "hysets_basin_shapes.shp"
# )
# wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
# wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets], ignore_index=True)
wspolygon.rename(columns={'GaugeID': 'gauge_id'}, inplace=True)
wspolygon.set_index("gauge_id", inplace=True)

# %% #######################################################
# Loading the data
############################################################
print("Loading signatures results file ...")
df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom.csv"),
    index_col="gauge_id",
)

#Set inf values to na
df_sigs.replace([np.inf, -np.inf], np.nan, inplace=True)


# _df_sigs = _df_sigs.drop(
#     columns=["gauge_name", "country", "gauge_lat", "gauge_lon", "area"]
# ).join(attrs_caravan, how="left")
# df_sigs = _df_sigs.join(eco_caravan, how="left")

df_sigs = wspolygon.join(df_sigs, how="right")

#######################################################
# Preprocess the data
#######################################################
print("Preprocess the data ...")

# Calculate some signatures
df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["avg_IE_SE_thresh"] = (df_sigs["IE_thresh"] + df_sigs["SE_thresh"]) / 2
df_sigs["avg_IE_SE_signif"] = (
    df_sigs["IE_thresh_signif"] + df_sigs["SE_thresh_signif"]
) / 2
#df_sigs["avg_IE_SE_thresh"].iloc[df_sigs["avg_IE_SE_thresh"] > 300] = np.nan
df_sigs.loc[df_sigs["avg_IE_SE_thresh"] > 300, "avg_IE_SE_thresh"] = np.nan

# Get the percentile
def below_thresh_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


print("Calculate signature percentiles ...")

for sigs_name in plot_sigs_config["column_name"]:
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    if "_signif" in sigs_name:
        df_sigs[sigs_name + "_perc"] = below_thresh_percentile(df_sigs[sigs_name], 0.05)
    else:
        df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100

# %%
df_sigs = df_sigs.to_crs("EPSG:4326")
df_sigs.to_file(
    os.path.join(out_dir, "out_calc_All_custom_postprocess.gpkg"),
    driver="GPKG"
)
# %% ######################
# FUNCTIONS
##########################

print("Define Functions ...")


def convert_3035_to_4326(x, y):
    # Initialize the transformer. always_xy=True ensures the output is always (Longitude, Latitude)
    transformer = pyproj.Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)

    # Perform the transformation
    lon, lat = transformer.transform(x, y)

    return lat, lon


def plot_sig_map(df, sig_name, overlay_layer, stats="normal", plot_mode="polygon"):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(6, 6))
    # fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add a legend
    overlay_layer.plot(
        ax=ax,
        edgecolor="grey",
        facecolor="none",
        linewidth=0.5,
        aspect=1.1,
        zorder=100,
    )

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
        print(sig_name)
        #print(plot_sigs_config.loc[plot_sigs_config["column_name"] == sig_name])
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name]
        llim = plot_config["lower_lim"]
        ulim = plot_config["upper_lim"]
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
    # cmap = plt.cm.YlGnBu
    if "diff_" in sig_name:
        cmap = plt.cm.RdBu_r
    norm = mpl.colors.Normalize(vmin=llim, vmax=ulim)

    if plot_mode == "scatter":

        lat1, lon1 = convert_3035_to_4326(df["Xcoord"], df["Ycoord"])
        plot_obj = ax.scatter(
            lon1,
            lat1,
            c=c_data,
            cmap=cmap,
            marker="o",
            # edgecolors="grey",
            s=7,
            alpha=0.5,
            zorder=99,
            vmin=llim,
            vmax=ulim,
        )
        cbar = plt.colorbar(plot_obj, ax=ax, shrink=0.5)
        cbar.set_label(cbar_label, rotation=270, labelpad=30)
    elif plot_mode == "polygon":
        df_sorted = df.sort_values("Area_km2", ascending=False)
        plot_obj = df_sorted.plot(
            ax=ax,
            column=sig_name,
            cmap=cmap,
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

    #ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    ax.set_title(title_label)

    plt.tight_layout(pad=1.5)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, out_file_name), dpi=300)


# %% ######################
#
#  Plot signature value map
#
##########################

print(" Plot signature value map ...")

# _____________________________________________________________________________
# Plot signature value map
# For testing
plot_sig_map(
    df_sigs,
    "BFI",
    ecoregion_overlay,
    stats="normal",
    plot_mode="polygon",
)

# %% For all signatures
for sigs_name in tqdm(
    plot_sigs_config.column_name, desc="Plotting maps of signature values", leave=False
):
    try:
        plot_sig_map(
            df_sigs, sigs_name, ecoregion_overlay, stats="normal", plot_mode="scatter"
        )
        plot_sig_map(
            df_sigs, sigs_name, ecoregion_overlay, stats="normal", plot_mode="polygon"
        )
    except Exception as e:
        print(f"{sigs_name}: {e}")


# %%

########################################################################################
#
# Plot the bivariate map
# Color map and the idea from Datawim: https://www.datawim.com/post/creating-professional-bivariate-maps-in-r/
#
########################################################################################


print(" Plot bivariate maps ...")

# Functions
# Get quantile & bivariate classes of data
def get_bivariate_class(df, sig1, sig2, sig1_label, sig2_label):
    df_clean = df.dropna(subset=[sig1.column_name, sig2.column_name]).copy()

    # Use custom bins for percentile columns
    for sig, label in [(sig1, sig1_label), (sig2, sig2_label)]:
        col_name = sig.column_name
        class_col = col_name + "_class"

        if "_perc" in col_name:
            # Use fixed percentile bins (0, 25, 50, 75, 100) for percentile columns
            # Already in percentiles, so use fixed bins
            bins = [0, 25, 50, 75, 100]
            df_clean[class_col] = pd.cut(
                df_clean[col_name], bins=bins, labels=label, include_lowest=True
            )
        else:
            # Use quantile-based binning for non-percentile columns
            # Not in percentiles, so use quantiles
            df_clean[class_col] = pd.qcut(
                df_clean[col_name], q=len(label), labels=label
            )

    df_clean["bivariate_class"] = (
        df_clean[sig1.column_name + "_class"].astype(str)
        + "-"
        + df_clean[sig2.column_name + "_class"].astype(str)
    )

    df_clean["color"] = df_clean["bivariate_class"].apply(
        lambda x: patch_colors[int(x.split("-")[1]) - 1][int(x.split("-")[0]) - 1]
    )

    return df_clean


def plot_bivariate_map(df, sig1, sig2, overlay_layer, fig_dir, plot_mode="polygon"):
    # Set up the map
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add map features
    if plot_mode == "scatter":
        lat1, lon1 = convert_3035_to_4326(df["Xcoord"], df["Ycoord"])
        ax.scatter(
            lon1,
            lat1,
            color=df["color"],
            marker="o",
            s=7,
            alpha=0.5,
        )
    elif plot_mode == "polygon":
        # Add an area column (if not already present)
        df["area"] = df.geometry.area

        # Sort by area in descending order so smaller polygons are plotted last
        df_sorted = df.sort_values("area", ascending=False)

        df_sorted.plot(ax=ax, color=df["color"], linewidth=0.2, alpha=0.5)

    # Add the BORDERS feature first
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="k", alpha=0.5)

    # Add the land feature with edgecolor set to black
    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
    )
    ax.add_feature(
        land,
        facecolor="none",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=0.5,  # Optionally adjust linewidth for edges
    )

    # Add a legend
    overlay_layer.plot(
        ax=ax,
        edgecolor="grey",
        facecolor="none",
        linewidth=0.5,
        aspect=1.1,
        zorder=100,
    )

    title_label = f"Bivariate map of {sig1.label} vs. {sig2.label}"
    ax.set_title(title_label)
    # Set extent to CONUS
    #ax.set_extent([-125.5, -66.95, 24.396308, 47.5])

    # Display the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            fig_dir, f"bivar_{sig1.column_name}_{sig2.column_name}_{plot_mode}.png"
        ),
        dpi=300,
    )


# Create a function to draw a bivariate legend
def create_bivariate_legend(colors, x_label, y_label, x_ticks, y_ticks, fig_dir):
    fig, ax = plt.subplots(figsize=(4, 4))

    # Add colored patches for each bivariate class
    for j, row in enumerate(colors):
        for i, color in enumerate(row):
            # Place the rows in the order they appear (smaller values at the bottom)
            # Plot the rectangle in the i-th color in the j-th row
            rect = Rectangle((i, j), 1, 1, facecolor=color, edgecolor="none")
            ax.add_patch(rect)

    # Set axis labels
    ax.set_xlabel(x_label, fontsize=12, labelpad=10)
    ax.set_ylabel(y_label, fontsize=12, labelpad=10)

    # # Set tick positions and labels
    ax.set_xticks([0.5 + i for i in range(len(colors[0]))])
    ax.set_xticklabels(x_ticks, fontsize=10)
    ax.set_yticks([0.5 + i for i in range(len(colors))])
    ax.set_yticklabels(y_ticks, fontsize=10)  # Reverse order for Y-axis

    # Remove gridlines and spines
    ax.set_xlim(0, len(colors[0]))
    ax.set_ylim(0, len(colors))
    ax.tick_params(left=False, bottom=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.grid(False)

    # Display the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(fig_dir, f"bivar_{sig1.column_name}_{sig2.column_name}_legend.png")
    )


def update_column_name(signal):
    """
    Updates the column_name attribute of the signal to use percentile, if it is threshold-based signatures
    Parameters:
    - signal: An object with `label` and `column_name` attributes.
    """
    label_to_column = {
        "IE_thresh_signif": "IE_thresh_signif_perc",
        "SE_thresh_signif": "SE_thresh_signif_perc",
        "Storage_thresh_signif": "Storage_thresh_signif_perc",
        "avg_IE_SE_signif": "avg_IE_SE_signif_perc",
    }
    # print(signal.column_name)

    print(
        f"Relabelling for: {signal.column_name}"
    )

    if signal.column_name in label_to_column:
        signal.column_name = label_to_column[signal.column_name]
        signal.label = sig1.label.replace("(p-value)", "significance")


# ______________________________________________________
# Preparation, do not change here
patch_colors = [
    ["#D3D3D3", "#D6B3A0", "#D9926A", "#DD6A29"],
    ["#9CC4D2", "#9EA69F", "#A08769", "#A36229"],
    ["#5FB2D1", "#60979F", "#617B69", "#635929"],
    ["#159DD0", "#15869E", "#176D68", "#174F28"],
]
cmap = ListedColormap(patch_colors)

# Labels for quantiles (low-->high)
labels = [1, 2, 3, 4]
dir_label = ["low", "", "", "high"]

# Reversed labels for quantiles (high --> low)
labels_rev = [
    4,
    3,
    2,
    1,
]
# Label low values as 4, so that it gets assigned to (x,y)=(i,4) or (4,j) in the quadrant
dir_label_rev = ["high", "", "", "low"]


# CHANGE HERE ################

processes = [
    "Baseflow",
    "Water balance losses",
    "High storage capacity",
 #   "Infiltration Excess Overlandflow",
 #   "Saturation Excess Overlandflow",
    "Seasonal variability",
 #   "IE vs SE significance",
 #   "IE vs SE (SSF2 & GW) significance",
 #   "SSF1 vs SSF2 & GW significance",
    "Overland Flow",
]

for process_name in tqdm(
    processes, desc="Plotting bivariate maps of process hypothesis", leave=False
):
    # For checking the items
    process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]
    print(process_columns)

    ###############################
    # Get the process signatures
    ###############################

    # For Baseflow plots
    if process_name == "Baseflow":
        sig2 = process_columns[
            process_columns["column_name"] == "BFI"
        ].squeeze()  # Y variable, BFI
        sig1 = process_columns[
            process_columns["column_name"] == "BaseflowRecessionK"
        ].squeeze()  # X variable, Baseflow Recession K

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label
    ###############################
    # For Water loss to deep GW or ET

    if process_name == "Water balance losses":
        sig2 = process_columns[
            process_columns["column_name"] == "EventRR"
        ].squeeze()  # Y variable, Total RR
        sig1 = process_columns[
            process_columns["column_name"] == "TotalRR"
        ].squeeze()  # X variable, Event RR

        sig1_label = labels
        sig2_label = labels_rev

        sig1_dir = dir_label
        sig2_dir = dir_label_rev
    ###############################
    # For Storage capacity and retention

    if process_name == "High storage capacity":
        sig1 = process_columns[
            process_columns["column_name"] == "RecessionParameters_b"
        ].squeeze()  # X variable, RecessionParameters_b
        sig2 = process_columns[
            process_columns["column_name"] == "AverageStorage"
        ].squeeze()  # Y variable, AverageStorage

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        # Higher b (=high nonlinearity) means multiple storages, so reverse the direction
        sig2_dir = dir_label

    ###############################
    # For Infiltration Excess Overlandflow

    if process_name == "Infiltration Excess Overlandflow":
        sig1 = process_columns.loc[
            process_columns.column_name == "IE_thresh_signif"
        ].squeeze()  # X variable
        sig2 = process_columns.loc[
            process_columns.column_name == "IE_thresh"
        ].squeeze()  # Y variable

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

    ###############################

    # For Saturation Excess Overlandflow

    if process_name == "Saturation Excess Overlandflow":
        sig1 = process_columns.loc[
            process_columns.column_name == "Storage_thresh_signif"
        ].squeeze()  # X variable, IE_thresh_signif
        sig2 = process_columns.loc[
            process_columns.column_name == "Storage_thresh"
        ].squeeze()  # Y variable, IE_thresh

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

    ###############################

    # For ET impacts on storage and baseflow
    if process_name == "Seasonal variability":
        sig1 = process_columns.loc[
            process_columns.column_name == "VariabilityIndex"
        ].squeeze()  # X variable, VariabilityIndex
        # sig2 = process_columns.loc[
        #     process_columns.column_name == "Recession_a_Seasonality"
        # ].squeeze()  # Y variable,
        sig2 = process_columns.loc[
            process_columns.column_name == "Recession_a_Seasonality"
        ].squeeze()  # Y variable,

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label
    ###############################

    # For Saturation Excess Overlandflow

    if process_name == "IE vs SE significance":
        sig2 = process_columns[
            process_columns["column_name"] == "IE_thresh_signif"
        ].squeeze()
        sig1 = process_columns[
            process_columns["column_name"] == "SE_thresh_signif"
        ].squeeze()

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label

    # For Saturation Excess Overlandflow

    if process_name == "IE vs SE (SSF2 & GW) significance":
        sig2 = process_columns[
            process_columns["column_name"] == "IE_thresh_signif"
        ].squeeze()
        sig1 = process_columns[
            process_columns["column_name"] == "Storage_thresh_signif"
        ].squeeze()

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label

    # For SSF1 vs SSF2 & GW significance
    if process_name == "SSF1 vs SSF2 & GW significance":
        sig2 = process_columns[
            process_columns["column_name"] == "SE_thresh_signif"
        ].squeeze()
        sig1 = process_columns[
            process_columns["column_name"] == "Storage_thresh_signif"
        ].squeeze()

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label

    if process_name == "Overland Flow":
        sig1 = process_columns.loc[
            process_columns.column_name == "avg_IE_SE_signif"
        ].squeeze()  # X variable
        sig2 = process_columns.loc[
            process_columns.column_name == "avg_IE_SE_thresh"
        ].squeeze()  # Y variable

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

    # If looking at the significance of the threshold values,
    # use the percentile columns, instead of the original p-values
    update_column_name(sig1)
    update_column_name(sig2)

    print(
        f"Plotting the bivariate map for Y: {sig2.column_name} & X: {sig1.column_name}"
    )

    #####################################################
    # Plot the bivariate map
    #####################################################

    # Get the bivariate class of data
    df_sigs_clean = get_bivariate_class(df_sigs, sig1, sig2, sig1_label, sig2_label)

    # Plot the bivariate map
    plot_bivariate_map(
        df_sigs_clean, sig1, sig2, ecoregion_overlay, fig_dir, plot_mode="polygon"
    )
    plot_bivariate_map(
        df_sigs_clean, sig1, sig2, ecoregion_overlay, fig_dir, plot_mode="scatter"
    )

    # Create the legend
    # Define axis labels and tick labels

    x_label = f"{sig1.label} {sig1.unit}"
    y_label = f"{sig2.label} {sig2.unit}"
    x_ticks = sig1_dir
    y_ticks = sig2_dir
    create_bivariate_legend(patch_colors, x_label, y_label, x_ticks, y_ticks, fig_dir)


# %%

# Create custom legend patches
from matplotlib.patches import Patch


def plot_process_dominance_map():
    """
    Create a map showing only 1-1 class (high in both variables) watersheds for
    Baseflow and Overland Flow processes with different colors.
    """
    # Set up the map
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add base map features
    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
    )
    ax.add_feature(
        land,
        facecolor="lightgray",
        edgecolor="black",
        linewidth=0.5,
    )
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="k", alpha=0.5)

    # Process Baseflow data
    sig1_bf = plot_sigs_config[
        plot_sigs_config["column_name"] == "BaseflowRecessionK"
    ].squeeze()
    sig2_bf = plot_sigs_config[plot_sigs_config["column_name"] == "BFI"].squeeze()

    # Process Overland Flow data
    sig1_of = plot_sigs_config[
        plot_sigs_config["column_name"] == "avg_IE_SE_signif"
    ].squeeze()
    sig2_of = plot_sigs_config[
        plot_sigs_config["column_name"] == "avg_IE_SE_thresh"
    ].squeeze()

    # Update column names for threshold values
    update_column_name(sig1_of)

    # Get the bivariate class for each process
    df_baseflow = get_bivariate_class(df_sigs, sig1_bf, sig2_bf, labels, labels)
    df_overland = get_bivariate_class(df_sigs, sig1_of, sig2_of, labels_rev, labels)
    df_baseflow.sort_values("Area_km2", ascending=False, inplace=True)
    df_overland.sort_values("Area_km2", ascending=False, inplace=True)

    # Define the classes to include with their alpha values
    classes_alpha = {
        "1-4": 0.75,  # Strongest class - highest alpha
        "1-3": 0.5,  # Medium-high class
        "2-3": 0.25,  # Medium-low class
        "2-4": 0.5,  # Lowest class - most transparent
    }

    legend_elements = []

    # Plot each group
    for df, process, color in [
        (df_baseflow, "Baseflow", "tab:blue"),
        (df_overland, "Overland Flow", "tab:orange"),
    ]:
        # Plot each class with different transparency
        for class_name, alpha in classes_alpha.items():
            df_class = df[df["bivariate_class"] == class_name].copy()
            df_class.sort_values("Area_km2", ascending=False, inplace=True)

            if class_name == "1-4":
                legend_label = f"{process}"
                legend_elements.append(
                    Patch(
                        facecolor=color,
                        alpha=1.0,
                        edgecolor="white",
                        label=legend_label,
                    )
                )

            if len(df_class) > 0:
                df_class.plot(
                    ax=ax,
                    color=color,
                    edgecolor="white",
                    linewidth=0.2,
                    alpha=alpha,
                    zorder=100,
                )
                print(f"{process_name} class {class_name}: {len(df_class)} watersheds")

    # Add ecoregion overlay
    ecoregion_overlay.plot(
        ax=ax,
        edgecolor="grey",
        facecolor="none",
        linewidth=0.5,
        aspect=1.1,
        zorder=5,
    )

    # Add legend and title
    ax.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=10,
    )

    ax.set_title("Dominant Processes")

    # Set extent to CONUS
    #ax.set_extent([-125.5, -66.95, 24.396308, 47.5])

    # Display the map
    plt.tight_layout()
    plt.savefig(
        os.path.join(fig_dir, "dominant_process_map.png"), dpi=300, bbox_inches="tight"
    )

    # Also create a summary stats
    print(f"Baseflow dominant watersheds: {len(df_baseflow)}")
    print(f"Overland Flow dominant watersheds: {len(df_overland)}")

    return fig, ax


# Run the function
plot_process_dominance_map()
# %%
