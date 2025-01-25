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
# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20240609_tunedparams"
plot_sigs_config_path = "plot_sigs_config.csv"
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

fig_dir = os.path.join(out_dir, "figs")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)
# %%
# ____________________________________________________________________________________
# Load overlay layer for plotting
_ecoregion_overlay = gpd.read_file(
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\EcoRegions\NA_CEC_Eco_Level1.shp"
)
_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
# %%
# ____________________________________________________________________________________
# Load data
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
_df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt.csv"), index_col="gauge_id"
)
# _df_sigs = _df_sigs.join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")

# %%
wspolygon_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles\camels\camels_basin_shapes.shp"
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles\hysets\hysets_basin_shapes.shp"
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets], ignore_index=True)
wspolygon.set_index("gauge_id", inplace=True)

# %%
df_sigs = wspolygon.join(df_sigs, how="right")
# %%
# Get the percentile
for sigs_name in plot_sigs_config["column_name"]:
    # Get df[sigs_name]
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100


# %% ######################
# FUNCTIONS
##########################


def plot_sig_map(df, sig_name, overlay_layer, stats="normal", plot_mode="scatter"):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add a legend
    # overlay_layer.plot(
    #     ax=ax,
    #     edgecolor="black",
    #     facecolor="none",
    #     linewidth=0.5,
    #     aspect=1.1,
    #     zorder=100,
    # )

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="darkgrey",  # Set land color to light gray
    )
    ax.add_feature(land)

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
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
            alpha=0.8,
            zorder=99,
            vmin=llim,
            vmax=ulim,
        )
        cbar = plt.colorbar(plot_obj, ax=ax, shrink=0.5)
        cbar.set_label(cbar_label, rotation=270, labelpad=30)
    elif plot_mode == "polygon":
        plot_obj = df.plot(
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

    ax.set_title(title_label)

    # Adding a colorbar

    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, out_file_name))


# %%
# %% ######################
# Plot signature value map
##########################

# _____________________________________________________________________________
# Plot signature value map
# For testing
# plot_sig_map(df_sigs, "TotalRR", ecoregion_overlay, stats="normal", plot_mode="polygon")

for sigs_name in plot_sigs_config.column_name:
    try:
        plot_sig_map(
            df_sigs, sigs_name, ecoregion_overlay, stats="normal", plot_mode="scatter"
        )
        plot_sig_map(
            df_sigs, sigs_name, ecoregion_overlay, stats="normal", plot_mode="polygon"
        )
    except:
        print(f"{sigs_name} is not in the prediction")

# %%
# ______________________________________________________________________________
# Plot the percentile map
# For testing
# plot_sig_map(df_sigs, "TotalRR", ecoregion_overlay, stats="normal")
for sigs_name in plot_sigs_config.column_name:
    try:
        plot_sig_map(
            df_sigs,
            sigs_name,
            ecoregion_overlay,
            stats="percentile",
            plot_mode="scatter",
        )
        plot_sig_map(
            df_sigs,
            sigs_name,
            ecoregion_overlay,
            stats="percentile",
            plot_mode="polygon",
        )
    except:
        print(f"{sigs_name} is not in the prediction")

# %%
# %% ######################
# Plot signature-process interpretation map
##########################

# ______________________________________________________________________________
# Plot the average percentile per processes
# process_name = "Baseflow"
# process_name = "Saturation Excess Overlandflow"  # "Infiltration Excess Overlandflow"
# process_name = "Storage capacity and retention"  # "Water loss to deep GW or ET"
process_name = "ET impacts on storage and baseflow"
process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]
process_columns


# %%
# Recalculate the percentiles based on aggregation
def recalculate_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


percentiles = []

for _, row in process_columns.iterrows():
    column_name = row["column_name"]
    relationship = row["relationship"]
    percentile_column = column_name + "_perc"

    if relationship == "pos":
        percentiles.append(df_sigs[percentile_column])
    elif relationship == "neg":
        percentiles.append(100 - df_sigs[percentile_column])
    elif "thresh" in relationship:
        # Extract the threshold value from the relationship string
        threshold = float(relationship.split(":")[1])
        recalculated_percentile = recalculate_percentile(
            df_sigs[column_name], threshold
        )
        percentiles.append(recalculated_percentile)

# Combine the percentiles and calculate the average
# Do not calculate the median percentile, if there is nan
df_sigs[process_name + "_medperc"] = pd.concat(percentiles, axis=1).median(
    axis=1, skipna=False
)
df_sigs

# %%
plot_sig_map(
    df_sigs, process_name, ecoregion_overlay, stats="process_perc", plot_mode="scatter"
)
plot_sig_map(
    df_sigs, process_name, ecoregion_overlay, stats="process_perc", plot_mode="polygon"
)


# %% ________________________________________
# Plot error map
def plot_err_box(df, sig_name):
    sample_counts = df["ecoregion"].value_counts()
    valid_ecoregions = sample_counts[sample_counts >= 100].index
    df_filt = df[df["ecoregion"].isin(valid_ecoregions)].copy()
    df_filt["ecoregion_number"] = df_filt["ecoregion"].str.extract(r"(\d+)").astype(int)

    df_sorted = df_filt.sort_values("ecoregion_number")

    # Plot the boxplot using Seaborn
    ecoregion_colors = [
        "#9ACDCF",
        "#5DC05A",
        "#4DCAC2",
        "#BBDD90",
        "#FECE9F",
        "#FFDB71",
        "#D1E8BA",
        "#BBDD90",
    ]

    plt.figure(figsize=(12, 5))
    boxplot = sns.boxplot(
        x=f"{sig_name}_medperc",
        y="ecoregion",
        data=df_sorted,
        palette=ecoregion_colors,
        order=df_sorted["ecoregion"].unique(),
    )

    # Customize the plot
    boxplot.set_xlabel("Median percentile")
    boxplot.set_ylabel("Ecoregion")
    boxplot.set_title(sig_name)
    boxplot.set_xlim([0, 100])

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"medpercbox_{sig_name}.png"))
    plt.show()


plot_err_box(df_sigs, process_name)

# %% ________________________________________________________
# Plot the bivariate map
process_name = "Baseflow"
# process_name = "Saturation Excess Overlandflow"  # "Infiltration Excess Overlandflow"
# process_name = "Storage capacity and retention"  # "Water loss to deep GW or ET"
# process_name = "ET impacts on storage and baseflow"
process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]
process_columns
# %%
# Get the quantiles of each signatures
sig2 = process_columns.iloc[0]  # Y variable, BFI
sig1 = process_columns.iloc[1]  # X variable, Baseflow Recession K

df_sigs_clean = df_sigs.dropna(subset=[sig1.column_name, sig2.column_name]).copy()

labels = [1, 2, 3, 4]

sig1_label = labels
sig2_label = labels

dir_label = ["low", "", "", "high"]

sig1_dir = dir_label
sig2_dir = dir_label

df_sigs_clean[sig1.column_name + "_class"] = pd.qcut(
    df_sigs_clean[sig1.column_name], q=len(sig1_label), labels=sig1_label
)
df_sigs_clean[sig2.column_name + "_class"] = pd.qcut(
    df_sigs_clean[sig2.column_name], q=len(sig2_label), labels=sig2_label
)

df_sigs_clean["bivariate_class"] = (
    df_sigs_clean[sig1.column_name + "_class"].astype(str)
    + "-"
    + df_sigs_clean[sig2.column_name + "_class"].astype(str)
)

print(df_sigs_clean["bivariate_class"].unique())
# %%
# Step 2: Create a color palette for 16 bivariate classes
# Define colors from the example (4x4 grid)
patch_colors = [
    ["#D3D3D3", "#D6B3A0", "#D9926A", "#DD6A29"],  # Row 1 becomes Row 4
    ["#9CC4D2", "#9EA69F", "#A08769", "#A36229"],  # Row 2 becomes Row 3
    ["#5FB2D1", "#60979F", "#617B69", "#635929"],  # Row 3 becomes Row 2
    ["#159DD0", "#15869E", "#176D68", "#174F28"],  # Row 4 becomes Row 1
]


# Create a function to draw a bivariate legend
def create_bivariate_legend(colors, x_label, y_label, x_ticks, y_ticks):
    fig, ax = plt.subplots(figsize=(4, 4))

    # Add colored patches for each bivariate class
    for i, row in enumerate(colors):
        for j, color in enumerate(row):
            # Place the rows in the order they appear (smaller values at the bottom)
            rect = Rectangle((j, i), 1, 1, facecolor=color, edgecolor="none")
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
    plt.show()


# Define axis labels and tick labels
x_label = f"{sig1.label} {sig1.unit}"
y_label = f"{sig2.label} {sig2.unit}"
x_ticks = sig1_dir
y_ticks = sig2_dir

# Create the legend
create_bivariate_legend(patch_colors, x_label, y_label, x_ticks, y_ticks)

cmap = ListedColormap(patch_colors)
# %%
# Step 3: Map bivariate classes to colors
df_sigs_clean["color"] = df_sigs_clean["bivariate_class"].apply(
    lambda x: patch_colors[int(x.split("-")[1]) - 1][int(x.split("-")[0]) - 1]
)

# Step 4: Plot the bivariate map

# Set up the map
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

# Add map features
df_sigs_clean.plot(ax=ax, color=df_sigs_clean["color"], linewidth=0.2, alpha=0.5)


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

title_label = f"Bivariate map of {sig1.label} vs. {sig2.label}"
ax.set_title(title_label)
# Set extent to CONUS
ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
# Display the plot
plt.tight_layout()
# plt.savefig(os.path.join(fig_dir, out_file_name))


# %%
