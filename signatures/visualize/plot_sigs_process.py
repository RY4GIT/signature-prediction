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

# %%

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
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\EcoRegions\NA_CEC_Eco_Level1.shp"
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
    f"attributes_other_camels.csv",
)
attrs_hysets_file = os.path.join(
    caravan_attrs_dir,
    "hysets",
    f"attributes_other_hysets.csv",
)
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
attrs_caravan = pd.concat([attrs_camels, attrs_hysets])

eco_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\EcoRegions\Ecoregion_camels.csv"
eco_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\EcoRegions\Ecoregion_hysets.csv"
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])

_df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom.csv"), index_col="gauge_id"
)
_df_sigs = _df_sigs.join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")

# %%
# Get the percentile
for sigs_name in plot_sigs_config["column_name"]:
    # Get df[sigs_name]
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    df_sigs[sigs_name + "_percentile"] = column_data.rank(pct=True) * 100


# %% ________________________________________________
def plot_sig_map(df, sig_name, overlay_layer, mode="normal"):

    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add a legend
    overlay_layer.plot(
        ax=ax,
        edgecolor="black",
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
        facecolor="lightgrey",  # Set land color to light gray
    )
    ax.add_feature(land)

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    # Add map features
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

    # Plotting the filtered data
    if mode == "normal":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name]
        llim = plot_config["lower_lim"]
        ulim = plot_config["upper_lim"]
        cbar_label = f'{plot_config["unit"]}'
        out_file_name = f"map_{sig_name}.png"
        title_label = f"{plot_config["label"]}"
    elif mode == "percentile":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name + "_percentile"]
        llim = 0
        ulim = 100
        cbar_label = "percentile"
        out_file_name = f"map_perc_{sig_name}.png"
        title_label = f"{plot_config["label"]}"
    elif mode == "process_perc":
        c_data = df[sig_name + "_medperc"]
        llim = 0
        ulim = 100
        cbar_label = "Median percentile"
        out_file_name = f"map_medperc_{sig_name}.png"
        title_label = sig_name

    scatter = ax.scatter(
        df["gauge_lon"],
        df["gauge_lat"],
        c=c_data,
        cmap="Blues",
        marker="o",
        # edgecolors="grey",
        s=5,
        alpha=0.8,
        zorder=99,
        vmin=llim,
        vmax=ulim,
    )
    ax.set_title(title_label)

    # Adding a colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
    cbar.set_label(cbar_label, rotation=270, labelpad=30)
    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, out_file_name))


# %%
# _____________________________________________________________________________
# Plot signature value map
# For testing
# plot_sig_map(df_sigs, "TotalRR", ecoregion_overlay, mode="normal")
for sigs_name in plot_sigs_config.column_name:
    try:
        plot_sig_map(df_sigs, sigs_name, ecoregion_overlay, mode="normal")
    except:
        print(f"{sigs_name} is not in the prediction")

# %%
# ______________________________________________________________________________
# Plot the percentile map
# For testing
# plot_sig_map(df_sigs, "TotalRR", ecoregion_overlay, mode="normal")
for sigs_name in plot_sigs_config.column_name:
    try:
        plot_sig_map(df_sigs, sigs_name, ecoregion_overlay, mode="percentile")
    except:
        print(f"{sigs_name} is not in the prediction")

# %%
# ______________________________________________________________________________
# Plot the average percentile per processes
process_name = "Baseflow"
baseflow_columns = plot_sigs_config[plot_sigs_config["process"] == "Baseflow"]
baseflow_columns
# %%
percentiles = []

for _, row in baseflow_columns.iterrows():
    column_name = row["column_name"]
    relationship = row["relationship"]
    percentile_column = column_name + "_percentile"

    if relationship == "pos":
        percentiles.append(df_sigs[percentile_column])
    elif relationship == "neg":
        percentiles.append(100 - df_sigs[percentile_column])

# Combine the percentiles and calculate the average
df_sigs[process_name + "_medperc"] = pd.concat(percentiles, axis=1).median(axis=1)
df_sigs

# %%
plot_sig_map(df_sigs, process_name, ecoregion_overlay, mode="process_perc")

# %%

# %%
df_sigs.ecoregion


# %%
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

# %%
