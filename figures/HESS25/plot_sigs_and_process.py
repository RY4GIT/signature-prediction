# %% Plot signatures from multiple sources (Caravan, GAGES-II, RF predictions)
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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
rf_out_dir = os.path.join(gdrive_dir, "out", "rf", "output_raraki_20250826_cluster_all")
fig_dir = os.path.join(
    gdrive_dir,
    "figs",
)

# Make Figure directory
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# Plotting config
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS_2025\plot_sigs_config.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# Drop Wu signatures from the plot_sigs_config
plot_sigs_config = plot_sigs_config[
    ~plot_sigs_config["column_name"].isin(
        ["R_Pint_RC", "R_Pvol_RC", "diff_RCPint_RCPvol"]
    )
]

# Conus extent
conus_extent = [-125.5, -66.95, 24.396308, 47.5]

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
print("Concatenating signatures results...")
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
df_sigs.to_csv(os.path.join(rf_out_dir, "sigs_predicted_observed_joined.csv"))

# %%
# Join the watershed polygons to the signatures data
df_sigs = wspolygon.join(df_sigs, how="right")


# %%
#######################################################
# Preprocess the data
#######################################################

# Calcaulte some signatures
# df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["avg_IE_SE_thresh"] = (df_sigs["IE_thresh"] + df_sigs["SE_thresh"]) / 2
df_sigs["avg_IE_SE_signif"] = (
    df_sigs["IE_thresh_signif"] + df_sigs["SE_thresh_signif"]
) / 2
df_sigs["avg_IE_SE_thresh"].iloc[df_sigs["avg_IE_SE_thresh"] > 300] = np.nan
# %%
# Mask out gauges with high snow
frac_snow_thresh = 0.2
low_snow = (
    (df_sigs["SNOW_PCT_PRECIP"] < frac_snow_thresh * 100)
    | (df_sigs["SNOW_PCT_PRECIP"].isna())
) | ((df_sigs["SNOWICENLCD06"] < frac_snow_thresh) | (df_sigs["SNOWICENLCD06"].isna()))
mask_cols = [
    "IE_thresh",
    "SE_thresh",
    "Storage_thresh",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "Storage_thresh_signif",
]
df_sigs[mask_cols] = df_sigs[mask_cols].mask(~low_snow)
# This line replaces values with NaN for any rows where low_snow is False
# low_snow is True for gauges with snow < threshold, False otherwise
# So ~low_snow is True for gauges with high snow, which get masked to NaN

print(
    f"{df_sigs['IE_thresh'].isna().sum()} gauges ({df_sigs['IE_thresh'].isna().sum() / len(df_sigs) * 100:.1f}%) have snow data above {frac_snow_thresh * 100}%"
)
# %%
print("Data length: ", len(df_sigs))
print("Baseflow data length: ", len(df_sigs[df_sigs["BFI"].notna()]))
print("Overlandflow data length: ", len(df_sigs[df_sigs["IE_thresh"].notna()]))


# %%
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


# %% ######################
# PLOTTING FUNCTIONS
##########################

# %% ######################
#
#  Plot signature value map
#
##########################


def plot_sig_map(
    df, sig_name, stats="normal", plot_mode="scatter", source=None, fig_dir=None
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
        facecolor="dimgrey",
        #        facecolor="#F4F5FA",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=1.0,  # Optionally adjust linewidth for edges
    )

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
    if "signif" in sig_name:
        cmap = plt.cm.Blues_r
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
        cax = inset_axes(
            ax, width="2.0%", height="35%", loc="lower right", borderpad=3.0
        )
        cbar = plt.colorbar(plot_obj, cax=cax)
        cbar.ax.tick_params(labelsize=10)
        cbar.set_label(cbar_label, rotation=270, labelpad=12)
    elif plot_mode == "polygon":
        df["area"] = df.geometry.area
        df.sort_values("area", ascending=False, inplace=True)
        plot_obj = df.plot(
            ax=ax,
            column=sig_name,
            cmap=cmap,
            alpha=0.5,
            vmin=llim,
            vmax=ulim,
            zorder=99,
        )

        # # Add a colorbar - repalce this as plot_sigs_hist
        # sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm._A = []  # Empty array for ScalarMappable
        # cax = inset_axes(
        #     ax, width="2.0%", height="35%", loc="lower right", borderpad=7.0
        # )
        # cbar = plt.colorbar(sm, cax=cax)
        # cbar.ax.tick_params(labelsize=18)
        # cbar.set_label(cbar_label, fontsize=18)

    ax.set_extent(conus_extent)
    for spine in ax.spines.values():
        spine.set_visible(False)
    # ax.set_title(title_label)

    # Output
    fig_sigs_dir = os.path.join(fig_dir, "supfig_sigs")
    if not os.path.exists(fig_sigs_dir):
        os.makedirs(fig_sigs_dir)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_sigs_dir, out_file_name), dpi=300)


# %% For all signatures except Wu
for sigs_name in tqdm(
    plot_sigs_config.column_name, desc="Plotting maps of signature values", leave=False
):
    try:
        warnings.filterwarnings("ignore")
        plot_sig_map(
            df_sigs,
            sigs_name,
            stats="normal",
            plot_mode="polygon",
            source="all",
            fig_dir=fig_dir,
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
# %%
# %%


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


def plot_bivariate_map(df, sig1, sig2, fig_dir, plot_mode="polygon"):
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
        df.sort_values("area", ascending=False, inplace=True)

        # Plot the polygons
        df.plot(
            ax=ax,
            color=df["color"],
            linewidth=0.2,
            alpha=0.4,
            zorder=99,
        )

    ax.set_extent(conus_extent)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Output directory
    fig_bivar_dir = os.path.join(fig_dir, "fig_processes")
    if not os.path.exists(fig_bivar_dir):
        os.makedirs(fig_bivar_dir)

    # Display the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            fig_bivar_dir,
            f"bivar_{sig1.column_name}_{sig2.column_name}_{plot_mode}.png",
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

    # Output directory
    fig_processes_dir = os.path.join(fig_dir, "fig_processes")
    if not os.path.exists(fig_processes_dir):
        os.makedirs(fig_processes_dir)

    # Display the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            fig_processes_dir, f"bivar_{sig1.column_name}_{sig2.column_name}_legend.png"
        )
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
#
# Plot the bivariate map of the processes
#
########################################################################################

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
    plot_bivariate_map(df_sigs_clean, sig1, sig2, fig_dir, plot_mode="polygon")

    # Create the legend
    # Define axis labels and tick labels

    x_label = f"{sig1.label} {sig1.unit}"
    y_label = f"{sig2.label} {sig2.unit}"
    x_ticks = sig1_dir
    y_ticks = sig2_dir
    create_bivariate_legend(patch_colors, x_label, y_label, x_ticks, y_ticks, fig_dir)


# %% ##################################
#
# Plot the process dominance map
#
##################################


def plot_process_dominance_map(df_sigs, plot_sigs_config, fig_dir):
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

    # Sort by area in descending order so smaller polygons are plotted last
    df_baseflow.sort_values("area", ascending=False, inplace=True)
    df_overland.sort_values("area", ascending=False, inplace=True)
    df_ET.sort_values("area", ascending=False, inplace=True)
    df_high_str.sort_values("area", ascending=False, inplace=True)

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
    # df_unclassified.sort_values("order", ascending=False, inplace=True)
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
                # For High storage capacity
                elif i == 3:
                    legend_elements.append(
                        Patch(
                            facecolor="none",
                            alpha=1.0,
                            edgecolor="#1B1212",
                            label=f"{process}",
                        )
                    )
                # For Baseflow and Overland flow
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
                # For Water balance losses
                if i == 2:
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
                # For Storage capacity
                elif i == 3:
                    df_class.plot(
                        ax=ax,
                        facecolor="none",
                        edgecolor="#1B1212",
                        linewidth=0.7,
                        alpha=0.8,
                        zorder=102,
                    )
                # For Baseflow and Overland flow
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

    # Add legend and title
    ax.legend(
        title="Dominant Process",
        handles=legend_elements,
        loc="lower right",
        fontsize=11,
    )

    # Set extent to CONUS
    ax.set_extent(conus_extent)

    # Set spines invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Output directory
    fig_dominant_process_dir = os.path.join(fig_dir, "fig_dominant_process")
    if not os.path.exists(fig_dominant_process_dir):
        os.makedirs(fig_dominant_process_dir)

    # Display the map
    plt.tight_layout()
    plt.savefig(
        os.path.join(fig_dominant_process_dir, "fig_dominant_process.png"),
        dpi=300,
        bbox_inches="tight",
    )

    # Also create a summary stats
    print(f"Baseflow dominant watersheds: {len(df_baseflow)}")
    print(f"Overland Flow dominant watersheds: {len(df_overland)}")

    return fig, ax


# Run the function
print("Plotting the process dominance map...")
plot_process_dominance_map(df_sigs, plot_sigs_config, fig_dir)

print("All plots completed. Figures saved in ", fig_dir)
