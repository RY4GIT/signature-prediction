# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import yaml
import geopandas as gpd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
import geopandas as gdp
from tqdm import tqdm
# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20250223_withWu"
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

caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
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
wspolygon_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles\camels\camels_basin_shapes.shp"
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles\hysets\hysets_basin_shapes.shp"
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
    columns=["gauge_name", "country", "gauge_lat", "gauge_lon", "area"]
).join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")

df_sigs = wspolygon.join(df_sigs, how="right")

#######################################################
# Preprocess the data
#######################################################

df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]


def below_thresh_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


# Get the percentile
for sigs_name in plot_sigs_config["column_name"]:
    # Get df[sigs_name]
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    if "_signif" in sigs_name:
        df_sigs[sigs_name + "_perc"] = below_thresh_percentile(df_sigs[sigs_name], 0.05)
    else:
        df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100


# %% ######################
# FUNCTIONS
##########################


def plot_sig_map(df, sig_name, overlay_layer, stats="normal", plot_mode="scatter"):
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
# For testing
plot_sig_map(df_sigs, "EventRR", ecoregion_overlay, stats="normal", plot_mode="polygon")
# %%
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

# # %%
# # ______________________________________________________________________________
# # Plot the percentile map
# # For testing
# # plot_sig_map(df_sigs, "TotalRR", ecoregion_overlay, stats="normal")
# for sigs_name in tqdm(
#     plot_sigs_config.column_name,
#     desc="Plotting maps of signature percentiles",
#     leave=False,
# ):
#     try:
#         plot_sig_map(
#             df_sigs,
#             sigs_name,
#             ecoregion_overlay,
#             stats="percentile",
#             plot_mode="scatter",
#         )
#         plot_sig_map(
#             df_sigs,
#             sigs_name,
#             ecoregion_overlay,
#             stats="percentile",
#             plot_mode="polygon",
#         )
#     except Exception as e:
#         print(f"{sigs_name}: {e}")

# %%
# %% ######################
#
# Plot signature-process interpretation map (linear combination of signatures)
#
##########################

# %%

########################################################################################
# Plot the bivariate map
# Color map and the idea from Datawim: https://www.datawim.com/post/creating-professional-bivariate-maps-in-r/
########################################################################################


# %% __________________________________________________
# Get quantile & bivariate classes of data
def get_bivariate_class(df, sig1, sig2, sig1_label, sig2_label):
    df_clean = df.dropna(subset=[sig1.column_name, sig2.column_name]).copy()

    # Use custom bins for percentile columns
    for sig, label in [(sig1, sig1_label), (sig2, sig2_label)]:
        col_name = sig.column_name
        class_col = col_name + "_class"

        if "_perc" in col_name:
            # Use fixed percentile bins (0, 25, 50, 75, 100) for percentile columns
            bins = [0, 25, 50, 75, 100]
            df_clean[class_col] = pd.cut(
                df_clean[col_name], bins=bins, labels=label, include_lowest=True
            )
        else:
            # Use quantile-based binning for non-percentile columns
            df_clean[class_col] = pd.qcut(
                df_clean[col_name], q=len(label), labels=label, duplicates="drop"
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

    # Add map features
    if plot_mode == "scatter":
        ax.scatter(
            df["gauge_lon"],
            df["gauge_lat"],
            color=df["color"],
            marker="o",
            s=5,
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
    }
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
# Label low values as 4, so that it gets assinged to (x,y)=(i,4) or (4,j) in the quadrant
dir_label_rev = ["high", "", "", "low"]


# CHANGE HERE ################

processes = [
    # "Baseflow",
    # "Water loss to deep GW or ET",
    # "Storage capacity and retention",
    # "Infiltration Excess Overlandflow",
    # "Saturation Excess Overlandflow",
    "ET impacts on storage and baseflow",
    # "IE vs SE significance",
    # "IE vs SE (SSF2 & GW) significance",
    # "SSF1 vs SSF2 & GW significance",
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

    if process_name == "Water loss to deep GW or ET":
        sig2 = process_columns[
            process_columns["column_name"] == "TotalRR"
        ].squeeze()  # Y variable, Total RR
        sig1 = process_columns[
            process_columns["column_name"] == "RR_Seasonality"
        ].squeeze()  # X variable, RR_Seaonality

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label
    ###############################
    # For Staoge capacity and retention

    if process_name == "Storage capacity and retention":
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
        ].squeeze()  # X variable, IE_thresh_signif
        sig2 = process_columns.loc[
            process_columns.column_name == "IE_thresh"
        ].squeeze()  # Y variable, IE_thresh

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

        # sig1 = process_columns.loc[
        #     process_columns.column_name == "SE_thresh_signif"
        # ].squeeze()  # X variable, IE_thresh_signif
        # sig2 = process_columns.loc[
        #     process_columns.column_name == "SE_thresh"
        # ].squeeze()  # Y variable, IE_thresh

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

    ###############################

    # For ET impacts on storage and baseflow
    if process_name == "ET impacts on storage and baseflow":
        sig1 = process_columns.loc[
            process_columns.column_name == "VariabilityIndex"
        ].squeeze()  # X variable, VariabilityIndex
        # sig2 = process_columns.loc[
        #     process_columns.column_name == "Recession_a_Seasonality"
        # ].squeeze()  # Y variable,
        sig2 = process_columns.loc[
            process_columns.column_name == "RR_Seasonality"
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

    # If looking at the significance of the threshold values, use the percentile columns, instead of the original p-values
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
