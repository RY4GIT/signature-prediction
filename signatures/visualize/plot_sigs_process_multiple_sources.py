# %%
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Rectangle, Patch
import matplotlib as mpl

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings


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
out_dir = os.path.join(gdrive_dir, "out", "signatures", "caravan_us_20250525")
out_dir_gages2 = os.path.join(gdrive_dir, "out", "signatures", "gages2_20250608")
rf_out_dir = os.path.join(gdrive_dir, "out", "rf", "output_raraki_20250716_cluster_all")

# Plotting config
plot_sigs_config_path = "plot_sigs_config.csv"
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# Figure directory
fig_dir = os.path.join(rf_out_dir, "figs_sig_pred_obs")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

conus_extent = [-125.5, -66.95, 24.396308, 47.5]
# %%
# ____________________________________________________________________________________
# Load overlay layer for plotting
print("Loading overlay layer...")
_ecoregion_overlay = gpd.read_file(
    os.path.join(gdrive_dir, "data", "EcoRegions", "NA_CEC_Eco_Level2.shp")
)
_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
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
attrs_hysets_file = os.path.join(
    caravan_attrs_dir,
    "hysets",
    "attributes_other_hysets.csv",
)
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
attrs_caravan = pd.concat([attrs_camels, attrs_hysets])

eco_camels_file = os.path.join(
    gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_camels.csv"
)
eco_hysets_file = os.path.join(
    gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_hysets.csv"
)
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])

# %%
print("Loading Caravan watershed shapefiles...")
# cARAVAN 1.5 shapefile is somehow corrupted, so use Caravan 1.4
wspolygon_camels_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "camels", "camels_basin_shapes.shp"
)
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "hysets", "hysets_basin_shapes.shp"
)
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)


# %%
print("Loading GAGES2 watershed shapefiles...")
gages2_wspolygon_file = os.path.join(
    gdrive_dir, "data", "GAGES2", "GAGES_II_Geospa", "gages2_polygons_not_cara.shp"
)
gages2_wspolygon = gpd.read_file(gages2_wspolygon_file).to_crs(epsg=4326)
gages2_wspolygon["gauge_id"] = "gages2_" + gages2_wspolygon["GAGE_ID"].astype(
    str
).str.zfill(8)
# %%
print("Concatenating Caravan and GAGES2 watershed shapefiles...")
wspolygon = pd.concat(
    [
        wspolygon_camels,
        wspolygon_hysets,
        gages2_wspolygon.drop(columns=["AREA", "PERIMETER", "GAGE_ID", "usgs_gauge"]),
    ],
    ignore_index=True,
)
wspolygon.set_index("gauge_id", inplace=True)


# %% #######################################################
# Loading the data
############################################################
print("Loading signatures results file ...")

print("Loading signatures results file for Caravan ...")
_df_sigs_cara = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area.csv"),
    index_col="gauge_id",
)
_df_sigs_cara["source"] = "Caravan_obs"
_df_sigs_cara["order"] = 1

print("Loading signatures results file for GAGES2 ...")
_df_sigs_gages2 = pd.read_csv(
    os.path.join(out_dir_gages2, "out_calc_All_custom_filt_qc_snow.csv"),
)
_df_sigs_gages2["gauge_id"] = "gages2_" + _df_sigs_gages2["gauge_id"].astype(
    str
).str.zfill(8)
_df_sigs_gages2.set_index("gauge_id", inplace=True)
_df_sigs_gages2["source"] = "GAGES2_obs"
_df_sigs_gages2["order"] = 2

print("Loading signatures results from RF predictions (overlap, baddata basins)...")
_df_sigs_rf_overlap_baddata = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_gg2_baddata.csv"),
    index_col="gauge_id",
)
# Pivot the dataframe to make signature names into columns
_df_sigs_rf_overlap_baddata = _df_sigs_rf_overlap_baddata.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_overlap_baddata["source"] = "RF_overlap_baddata"
_df_sigs_rf_overlap_baddata["order"] = 3

print("Loading signatures results from RF predictions (only hys basins)...")
_df_sigs_rf_hys_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_hys_only = _df_sigs_rf_hys_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_hys_only["source"] = "RF_hys_only"
_df_sigs_rf_hys_only["order"] = 4

print("Loading signatures results from RF predictions (only GAGES2 basins)...")
_df_sigs_rf_gg2_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_gg2_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_gg2_only = _df_sigs_rf_gg2_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_gg2_only["source"] = "RF_gg2_only"
_df_sigs_rf_gg2_only["order"] = 5

# %%
_df_sigs = pd.concat(
    [
        _df_sigs_cara,
        _df_sigs_gages2,
        _df_sigs_rf_overlap_baddata,
        _df_sigs_rf_hys_only,
        _df_sigs_rf_gg2_only,
    ]
)
_df_sigs = _df_sigs.drop(
    columns=["gauge_name", "country", "gauge_lat", "gauge_lon", "area"]
).join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")
df_sigs.to_csv(os.path.join(rf_out_dir, "predicted_observed_sigs_joined.csv"))


# %%
df_sigs = wspolygon.join(df_sigs, how="right")

# %% Check gages2_ basins are joined correctly
df_sigs[df_sigs["source"] == "GAGES2_obs"].head()
# %%
df_sigs.head()
# %%
print("Baseflow data length: ", len(df_sigs[df_sigs["BFI"].notna()]))
print("Overlandflow data length: ", len(df_sigs[df_sigs["IE_thresh"].notna()]))
# %%
#######################################################
# Preprocess the data
#######################################################

# Calcaulte some signatures
df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["avg_IE_SE_thresh"] = (df_sigs["IE_thresh"] + df_sigs["SE_thresh"]) / 2
df_sigs["avg_IE_SE_signif"] = (
    df_sigs["IE_thresh_signif"] + df_sigs["SE_thresh_signif"]
) / 2
df_sigs["avg_IE_SE_thresh"].iloc[df_sigs["avg_IE_SE_thresh"] > 300] = np.nan


# Get the percentile
def below_thresh_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


for sigs_name in plot_sigs_config["column_name"]:
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    if "_signif" in sigs_name:
        df_sigs[sigs_name + "_perc"] = below_thresh_percentile(df_sigs[sigs_name], 0.05)
    else:
        df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100


# # %%
# df_sigs.to_file(
#     os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area_postprocess.gpkg"),
#     driver="GPKG",
#     crs="EPSG:4326",
# )
# %%
#######################################################
# Plot the source
#######################################################
# Define source colors
source_colors = {
    "Caravan_obs": {"color": "lightgrey", "label": "Caravan (Observed)", "alpha": 0.4},
    "GAGES2_obs": {"color": "tab:blue", "label": "GAGES-II (Observed)", "alpha": 0.7},
    "RF_overlap_baddata": {
        "color": "tab:red",
        "label": "RF (Caravan+GAGES-II\noverlap)",
        "alpha": 0.7,
    },
    "RF_hys_only": {"color": "tab:orange", "label": "RF (Caravan only)", "alpha": 0.7},
    "RF_gg2_only": {"color": "#F0E442", "label": "RF (GAGES-II only)", "alpha": 0.7},
}


def plot_source(df, overlay_layer):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(12, 6))
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

    # Add map features
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

    # Create legend patches
    legend_patches = []
    for source in [
        "RF_gg2_only",
        "RF_hys_only",
        "RF_overlap_baddata",
        "GAGES2_obs",
        "Caravan_obs",
    ]:
        # Create a patch for each source
        patch = mpl.patches.Patch(
            facecolor=source_colors[source]["color"],
            edgecolor="black",
            alpha=1.0,
            label=source_colors[source]["label"],
        )
        legend_patches.append(patch)

        # Plot the data
        df_source = df[df["source"] == source].copy()
        df_source.sort_values("area", ascending=False, inplace=True)
        df_source.plot(
            ax=ax,
            color=source_colors[source]["color"],
            alpha=source_colors[source]["alpha"],
            zorder=99,
        )

    ax.set_extent(conus_extent)
    # ax.set_title("Sources")

    # Add custom legend
    ax.legend(
        title="Sources",
        handles=legend_patches[::-1],
        loc="lower right",
        bbox_to_anchor=(1.0, 0.0),
        ncol=1,
        fontsize=10,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout(pad=1.5)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "source_map.png"), dpi=300)


plot_source(df_sigs, ecoregion_overlay)
# %% ######################
# FUNCTIONS
##########################


def plot_sig_map(
    df, sig_name, overlay_layer, stats="normal", plot_mode="scatter", source=None
):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(12, 8))
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
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name]
        llim = plot_config["lower_lim"]
        ulim = plot_config["upper_lim"]
        cbar_label = f"{plot_config['unit']}"
        out_file_name = f"map_{sig_name}_{plot_mode}_{source}.png"
        title_label = f"{plot_config['label']} ({source})"
    elif stats == "percentile":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name + "_perc"]
        llim = 0
        ulim = 100
        cbar_label = "percentile"
        out_file_name = f"map_perc_{sig_name}_{plot_mode}_{source}.png"
        title_label = f"{plot_config['label']} ({source})"
    elif stats == "process_perc":
        c_data = df[sig_name + "_medperc"]
        llim = 0
        ulim = 100
        cbar_label = "Median percentile"
        out_file_name = f"map_medperc_{sig_name}_{plot_mode}_{source}.png"
        title_label = f"{sig_name} ({source})"

    # Create a colormap and normalize
    cmap = plt.cm.Blues
    # cmap = plt.cm.YlGnBu
    if "diff_" in sig_name:
        cmap = plt.cm.RdBu_r
    norm = mpl.colors.Normalize(vmin=llim, vmax=ulim)

    if plot_mode == "scatter":
        plot_obj = ax.scatter(
            df["gauge_lon"],
            df["gauge_lat"],
            c=c_data,
            cmap=cmap,
            marker="o",
            # edgecolors="grey",
            s=5,
            alpha=0.5,
            zorder=99,
            vmin=llim,
            vmax=ulim,
        )
        cbar = plt.colorbar(plot_obj, ax=ax, shrink=0.5)
        cbar.set_label(cbar_label, rotation=270, labelpad=30)
    elif plot_mode == "polygon":
        df_sorted = df.sort_values("area", ascending=False)
        df_sorted = df.sort_values("order", ascending=False)
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
# # For testing
# plot_sig_map(
#     df_sigs,
#     "StorageFromBaseflow",
#     ecoregion_overlay,
#     stats="normal",
#     plot_mode="scatter",
# )

# %% For all signatures
for sigs_name in tqdm(
    plot_sigs_config.column_name, desc="Plotting maps of signature values", leave=False
):
    try:
        warnings.filterwarnings("ignore")
        plot_sig_map(
            df_sigs,
            sigs_name,
            ecoregion_overlay,
            stats="normal",
            plot_mode="scatter",
            source="all",
        )
        plot_sig_map(
            df_sigs,
            sigs_name,
            ecoregion_overlay,
            stats="normal",
            plot_mode="polygon",
            source="all",
        )
    except Exception as e:
        print(f"{sigs_name}: {e}")

# # %% Plot the map by source
# for source in df_sigs["source"].unique():
#     for sigs_name in tqdm(
#         plot_sigs_config.column_name,
#         desc=f"Plotting maps of signature values for {source}",
#         leave=False,
#     ):
#         # Surpress the warnings.warn(
#         warnings.filterwarnings("ignore")
#         plot_sig_map(
#             df_sigs[df_sigs["source"] == source],
#             sigs_name,
#             ecoregion_overlay,
#             stats="normal",
#             plot_mode="polygon",
#             source=source,
#         )
# %%

########################################################################################
#
# Plot the bivariate map
# Color map and the idea from Datawim: https://www.datawim.com/post/creating-professional-bivariate-maps-in-r/
#
########################################################################################


########################################################################################
# Functions
########################################################################################
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
    fig = plt.figure(figsize=(12, 8))
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

    # Add map features
    if plot_mode == "scatter":
        ax.scatter(
            df["gauge_lon"],
            df["gauge_lat"],
            color=df["color"],
            marker="o",
            s=5,
            alpha=0.5,
            zorder=99,
        )
    elif plot_mode == "polygon":
        # Add an area column (if not already present)
        df["area"] = df.geometry.area

        # Sort by area in descending order so smaller polygons are plotted last
        df_sorted = df.sort_values("area", ascending=False)
        df_sorted = df.sort_values("order", ascending=False)

        df_sorted.plot(
            ax=ax,
            color=df["color"],
            linewidth=0.2,
            alpha=0.5,
            zorder=99,
        )

    # # Add a legend
    # overlay_layer.plot(
    #     ax=ax,
    #     edgecolor="grey",
    #     facecolor="none",
    #     linewidth=0.5,
    #     aspect=1.1,
    #     zorder=100,
    # )

    title_label = f"Bivariate map of {sig1.label} vs. {sig2.label}"
    ax.set_title(title_label)
    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])

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
        os.path.join(fig_dir, f"bivar_{sig1.column_name}_{sig2.column_name}_legend.pdf")
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
    if signal.column_name in label_to_column:
        signal.column_name = label_to_column[signal.column_name]
        signal.label = signal.label.replace("(p-value)", "significance")


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
# Label low values as 4, so that it gets assinged to (x,y)=(i,4) or (4,j) in the quadrant
dir_label_rev = ["high", "", "", "low"]


# End of "do not change"
# ______________________________________________________

# %% ########################################################################################

processes = [
    "Baseflow",
    "High storage capacity",
    "Water balance losses",
    "Seasonal variability",
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
    # For Staoge capacity and retention

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
    # For Water loss to deep GW or ET
    if process_name == "Water balance losses":
        sig2 = process_columns[
            process_columns["column_name"] == "TotalRR"
        ].squeeze()  # Y variable, Total RR
        sig1 = process_columns[
            process_columns["column_name"] == "EventRR"
        ].squeeze()  # X variable, EventRR

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
        sig2 = process_columns.loc[
            process_columns.column_name == "Recession_a_Seasonality"
        ].squeeze()  # Y variable,

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

    ###############################
    # For Overland Flow
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
def plot_process_dominance_map():
    """
    Create a map showing only 1-1 class (high in both variables) watersheds for
    Baseflow and Overland Flow processes with different colors.
    """
    # Set up the map
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add base map features
    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
    )
    ax.add_feature(
        land,
        facecolor="#F4F5FA",
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

    # Process Water balance loss data
    sig1_ET = (
        plot_sigs_config[plot_sigs_config["column_name"] == "TotalRR"].iloc[0].squeeze()
    )
    sig2_ET = plot_sigs_config[plot_sigs_config["column_name"] == "EventRR"].squeeze()

    # Process high storage region
    sig1_str = plot_sigs_config[
        plot_sigs_config["column_name"] == "RecessionParameters_b"
    ].squeeze()
    sig2_str = plot_sigs_config[
        plot_sigs_config["column_name"] == "AverageStorage"
    ].squeeze()

    # Update column names for threshold values
    update_column_name(sig1_of)

    # Get the bivariate class for each process
    df_baseflow = get_bivariate_class(df_sigs, sig1_bf, sig2_bf, labels, labels)
    df_overland = get_bivariate_class(df_sigs, sig1_of, sig2_of, labels_rev, labels)
    df_ET = get_bivariate_class(df_sigs, sig1_ET, sig2_ET, labels, labels_rev)
    df_high_str = get_bivariate_class(df_sigs, sig1_str, sig2_str, labels_rev, labels)
    #
    df_baseflow.sort_values("area", ascending=False, inplace=True)
    df_overland.sort_values("area", ascending=False, inplace=True)
    df_ET.sort_values("area", ascending=False, inplace=True)
    df_high_str.sort_values("area", ascending=False, inplace=True)
    #
    df_baseflow.sort_values("order", ascending=False, inplace=True)
    df_overland.sort_values("order", ascending=False, inplace=True)
    df_ET.sort_values("order", ascending=False, inplace=True)
    df_high_str.sort_values("order", ascending=False, inplace=True)

    # Define the classes to include with their alpha values
    classes_alpha = {
        "1-4": 0.75,  # Strongest class - highest alpha
        "1-3": 0.5,  # Medium-high class
        "2-3": 0.25,  # Medium-low class
        "2-4": 0.5,  # Lowest class - most transparent
    }

    class_list = ["1-4", "1-3", "2-3", "2-4"]

    # Get indices of watersheds that are not in any of the classified groups
    baseflow_mask = ~df_baseflow.index.isin(
        df_baseflow[df_baseflow["bivariate_class"].isin(class_list)].index
    )
    overland_mask = ~df_overland.index.isin(
        df_overland[df_overland["bivariate_class"].isin(class_list)].index
    )

    # Get watersheds that are unclassified in all three processes
    # Get common indices between all masks by aligning masks to df_sigs index first
    baseflow_aligned = pd.Series(baseflow_mask, index=df_baseflow.index).reindex(
        df_sigs.index
    )
    overland_aligned = pd.Series(overland_mask, index=df_overland.index).reindex(
        df_sigs.index
    )

    # Fill any NaN values with False
    baseflow_aligned = baseflow_aligned.fillna(False)
    overland_aligned = overland_aligned.fillna(False)

    # Get common indices where all masks are True
    common_indices = df_sigs.index[baseflow_aligned & overland_aligned]
    df_unclassified = df_sigs[df_sigs.index.isin(common_indices)]
    df_unclassified.sort_values("area", ascending=False, inplace=True)
    df_unclassified.sort_values("order", ascending=False, inplace=True)
    print(f"Unclassified watersheds: {len(df_unclassified)}")

    legend_elements = []

    # Plot each group

    df_unclassified.plot(
        ax=ax,
        color="lightgrey",
        edgecolor="white",
        linewidth=0.2,
        alpha=1.0,
        zorder=99,
    )

    for i, df, process, color in [
        (0, df_baseflow, "Baseflow", "royalblue"),
        (1, df_overland, "Overland Flow", "lightcoral"),
        (2, df_ET, "Water balance losses", None),
        (3, df_high_str, "High storage capacity", None),
    ]:
        # Plot each class with different transparency
        for class_name, alpha in classes_alpha.items():
            df_class = df[df["bivariate_class"] == class_name].copy()
            df_class.sort_values("area", ascending=False, inplace=True)

            # _______________________________________________________________________
            # Make legend elements
            if class_name == "1-4":
                # For Water balance losses
                if i == 2:
                    # Add unclassified legend element
                    legend_elements.append(
                        Patch(
                            facecolor="lightgrey",
                            alpha=1.0,
                            edgecolor="white",
                            label="Unclassified",
                        )
                    )
                    # Add water balance loss legend element
                    legend_elements.append(
                        Patch(
                            facecolor="none",
                            alpha=1.0,
                            edgecolor="dimgrey",
                            hatch="////",
                            label=f"{process}",
                        )
                    )
                # For Storage capacity
                elif i == 3:
                    legend_elements.append(
                        Patch(
                            facecolor="none",
                            alpha=1.0,
                            edgecolor="#1B1212",
                            label=f"{process}",
                        )
                    )
                else:
                    legend_elements.append(
                        Patch(
                            facecolor=color,
                            alpha=1.0,
                            edgecolor="white",
                            label=f"{process}",
                        )
                    )

            # _______________________________________________________________________
            # Plot watershed polygons
            if len(df_class) > 0:
                # For Water balance loss, only plot the 1-4 class
                if i == 2:
                    if class_name == "1-4":
                        with plt.rc_context({"hatch.linewidth": 0.01}):
                            df_class.plot(
                                ax=ax,
                                facecolor="none",
                                edgecolor="white",
                                linewidth=0.01,
                                alpha=0.3,
                                hatch="////",
                                zorder=101,
                            )
                    else:
                        None
                # For Storage capacity, plot all high 4 classes
                elif i == 3:
                    df_class.plot(
                        ax=ax,
                        facecolor="none",
                        edgecolor="#1B1212",
                        linewidth=0.7,
                        alpha=0.8,
                        zorder=102,
                    )
                # For Baseflow and Overland flow, plot all high 4 classes
                else:
                    df_class.plot(
                        ax=ax,
                        color=color,
                        edgecolor="white",
                        linewidth=0.2,
                        alpha=alpha,
                        zorder=100,
                    )
                print(f"{process} class {class_name}: {len(df_class)} watersheds")

    # # Add ecoregion overlay
    # ecoregion_overlay.plot(
    #     ax=ax,
    #     edgecolor="grey",
    #     facecolor="none",
    #     linewidth=0.5,
    #     aspect=1.1,
    #     zorder=5,
    # )

    # Add legend and title
    ax.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=10,
    )

    ax.set_title("(a) Dominant Processes", loc="left", fontweight="bold")

    # Set extent to CONUS
    ax.set_extent(conus_extent)

    # Set spines invisible
    ax.outline_patch.set_visible(False)

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


# %% Plot diff_RCPint_RCPvol separately


def plot_diff_RCPint_RCPvol(
    df, sig_name, overlay_layer, stats="normal", plot_mode="polygon", source=None
):
    fig = plt.figure(figsize=(12, 8))
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

    # Get plot fongi
    plot_config = plot_sigs_config.loc[
        plot_sigs_config["column_name"] == sig_name
    ].iloc[0]
    c_data = df[sig_name]
    llim = plot_config["lower_lim"]
    ulim = plot_config["upper_lim"]
    cbar_label = f"{plot_config['unit']}"
    out_file_name = f"map_{sig_name}_{plot_mode}_{source}.png"
    title_label = f"{plot_config['label']} ({source})"

    diagonal_colors = [
        "#159DD0",
        # "#2CA6D4",
        "#43B0D9",
        "#aeb5b1",
        "#E38753",
        # "#E0783E",
        "#DD6A29",
    ]

    # Create the colormap
    diag_cmap = LinearSegmentedColormap.from_list(
        "custom_diag_gradient", diagonal_colors
    )

    cmap = diag_cmap
    norm = mpl.colors.Normalize(vmin=llim, vmax=ulim)

    df_sorted = df.sort_values("area", ascending=False)
    df_sorted = df.sort_values("order", ascending=False)
    df_sorted.plot(
        ax=ax,
        column=sig_name,
        cmap=cmap,
        alpha=0.8,
        vmin=llim,
        vmax=ulim,
        zorder=99,
    )

    # Add a colorbar
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []  # Empty array for ScalarMappable
    cbar = plt.colorbar(sm, ax=ax, shrink=0.3)
    cbar.ax.tick_params(labelsize=18)  # Set font size
    cbar.set_ticks(np.linspace(llim, ulim, 5))
    cbar.set_label(cbar_label, rotation=270, labelpad=30)

    ax.set_title(title_label)
    ax.set_extent(conus_extent)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(fig_dir, out_file_name), dpi=300)


plot_diff_RCPint_RCPvol(
    df_sigs,
    "diff_RCPint_RCPvol",
    ecoregion_overlay,
    stats="normal",
    plot_mode="polygon",
    source="all",
)


# %%
# Add folium for interactive mapping
import folium
from folium import plugins


def plot_diff_RCPint_RCPvol_interactive(df, sig_name, stats="normal", source=None):
    """
    Create an interactive map for diff_RCPint_RCPvol using Folium with scatter points.

    Parameters:
    - df: DataFrame with the data
    - sig_name: Name of the signature column to plot
    - stats: Type of statistics to plot ("normal" or "percentile")
    - source: Source label for the title
    """

    # Filter out rows with missing data
    df_clean = df.dropna(subset=[sig_name, "gauge_lat", "gauge_lon"]).copy()

    # Get plot config
    plot_config = plot_sigs_config.loc[
        plot_sigs_config["column_name"] == sig_name
    ].iloc[0]

    c_data = df_clean[sig_name]
    llim = plot_config["lower_lim"]
    ulim = plot_config["upper_lim"]
    cbar_label = f"{plot_config['unit']}"
    title_label = f"Interactive Map: {plot_config['label']}"
    if source:
        title_label += f" ({source})"

    # Create a diverging colormap centered at 0
    from matplotlib.colors import TwoSlopeNorm
    import matplotlib.colors as mcolors

    # Use a diverging colormap (RdBu_r, coolwarm, RdYlBu, etc.)
    cmap = plt.get_cmap(
        "RdBu_r"
    )  # Red-Blue diverging, reversed so red=positive, blue=negative

    # Create a normalizer that centers at 0
    norm = TwoSlopeNorm(vmin=llim, vcenter=0, vmax=ulim)

    # Create a function to get hex colors from the normalized colormap
    def get_color_from_cmap(value):
        """Convert a value to a hex color using the diverging colormap centered at 0"""
        if pd.isna(value):
            return "#808080"  # Gray for NaN values

        # Normalize the value and get the color
        normalized_value = norm(value)
        rgba_color = cmap(normalized_value)

        # Convert RGBA to hex
        return mcolors.to_hex(rgba_color)

    # Create the base map centered on CONUS
    m = folium.Map(
        location=[39.8, -98.6],  # Center of CONUS
        zoom_start=4,
        tiles="OpenStreetMap",
    )

    # Add title as HTML
    title_html = f"""
                 <h3 align="center" style="font-size:16px"><b>{title_label}</b></h3>
                 """
    m.get_root().html.add_child(folium.Element(title_html))

    # Add circle markers for each point
    for idx, row in df_clean.iterrows():
        # Create popup content
        popup_content = f"""
        <b>Gauge ID:</b> {idx}<br>
        <b>{plot_config["label"]}:</b> {row[sig_name]:.3f} {plot_config["unit"]}<br>
        <b>RCPint:</b> {row["R_Pint_RC"]:.3f}<br>
        <b>RCPvol:</b> {row["R_Pvol_RC"]:.3f}<br>
        """

        # Get color for this value
        color = get_color_from_cmap(row[sig_name])

        # Add circle marker
        folium.CircleMarker(
            location=[row["gauge_lat"], row["gauge_lon"]],
            radius=6,
            tooltip=popup_content,
            color="white",
            weight=1,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
        ).add_to(m)

    # Create a simple diverging legend
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 160px; height: 100px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px">
    <p><b>{cbar_label}</b></p>
    <p><span style="color: {get_color_from_cmap(ulim)}">■</span> High ({ulim:.2f})</p>
    <p><span style="color: {get_color_from_cmap(0)}">■</span> Zero (0.00)</p>
    <p><span style="color: {get_color_from_cmap(llim)}">■</span> Low ({llim:.2f})</p>
    <p><i>Centered at 0</i></p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Save the interactive plot
    output_file = os.path.join(fig_dir, f"interactive_map_{sig_name}_{source}.html")
    m.save(output_file)
    print(f"Interactive map saved to: {output_file}")
    print("Open the HTML file in your web browser to view the interactive map.")

    return m


# Create interactive version
plot_diff_RCPint_RCPvol_interactive(
    df_sigs,
    "diff_RCPint_RCPvol",
    stats="normal",
    source="all",
)

# %% Plot the histogram of RCPint and RCPvol


def plot_RCP_histograms(df):
    """
    Plot histograms of RCPint, RCPvol, and their difference
    """
    # Filter data to remove NaN values
    df_clean = df.dropna(subset=["R_Pint_RC", "R_Pvol_RC", "diff_RCPint_RCPvol"]).copy()

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: Histograms of RCPint and RCPvol
    ax1.hist(
        df_clean["R_Pint_RC"],
        bins=50,
        alpha=0.7,
        label="RCPint",
        color="steelblue",
        edgecolor="black",
        linewidth=0.5,
    )
    ax1.hist(
        df_clean["R_Pvol_RC"],
        bins=50,
        alpha=0.7,
        label="RCPvol",
        color="orange",
        edgecolor="black",
        linewidth=0.5,
    )

    ax1.set_xlabel("Value", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.set_title("Distribution of RCPint and RCPvol", fontsize=14, fontweight="bold")
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Add vertical lines for means
    mean_rcpint = df_clean["R_Pint_RC"].mean()
    mean_rcpvol = df_clean["R_Pvol_RC"].mean()
    ax1.axvline(
        mean_rcpint,
        color="steelblue",
        linestyle="--",
        alpha=0.8,
        label=f"RCPint mean: {mean_rcpint:.3f}",
    )
    ax1.axvline(
        mean_rcpvol,
        color="orange",
        linestyle="--",
        alpha=0.8,
        label=f"RCPvol mean: {mean_rcpvol:.3f}",
    )

    # Panel 2: Histogram of difference
    ax2.hist(
        df_clean["diff_RCPint_RCPvol"],
        bins=50,
        alpha=0.8,
        color="forestgreen",
        edgecolor="black",
        linewidth=0.5,
    )

    ax2.set_xlabel("RCPint - RCPvol", fontsize=12)
    ax2.set_ylabel("Frequency", fontsize=12)
    ax2.set_title(
        "Distribution of RCPint - RCPvol Difference", fontsize=14, fontweight="bold"
    )
    ax2.grid(True, alpha=0.3)

    # Add vertical line at zero
    ax2.axvline(
        0, color="red", linestyle="-", linewidth=2, alpha=0.8, label="Zero difference"
    )

    # Add vertical line for mean difference
    mean_diff = df_clean["diff_RCPint_RCPvol"].mean()
    ax2.axvline(
        mean_diff,
        color="darkgreen",
        linestyle="--",
        alpha=0.8,
        label=f"Mean diff: {mean_diff:.3f}",
    )

    ax2.legend(fontsize=11)

    # Add statistics text box
    stats_text = f"""Statistics:
    N = {len(df_clean):,}
    Mean diff = {mean_diff:.3f}
    Std diff = {df_clean["diff_RCPint_RCPvol"].std():.3f}
    % Positive = {(df_clean["diff_RCPint_RCPvol"] > 0).mean() * 100:.1f}%
    % Negative = {(df_clean["diff_RCPint_RCPvol"] < 0).mean() * 100:.1f}%"""

    ax2.text(
        0.02,
        0.98,
        stats_text,
        transform=ax2.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    # Improve layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        os.path.join(fig_dir, "histogram_RCP_components.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()

    return fig


# Create the histogram plot
plot_RCP_histograms(df_sigs)

# %%
