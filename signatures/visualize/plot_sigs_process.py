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
len(wspolygon)
# %%
df_sigs = wspolygon.join(df_sigs, how="right")
# %%
# Get the percentile
for sigs_name in plot_sigs_config["column_name"]:
    # Get df[sigs_name]
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    df_sigs[sigs_name + "_percentile"] = column_data.rank(pct=True) * 100


# %% ________________________________________________
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
        c_data = df[sig_name + "_percentile"]
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
plot_sigs_config
# %%
# ______________________________________________________________________________
# Plot the average percentile per processes
# process_name = "Baseflow"
# process_name = "Saturation Excess Overlandflow"  # "Infiltration Excess Overlandflow"
# process_name = "Storage capacity and retention"  # "Water loss to deep GW or ET"
process_name = "ET impacts on storage and baseflow"
process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]
process_columns
# %%


def recalculate_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


percentiles = []

for _, row in process_columns.iterrows():
    column_name = row["column_name"]
    relationship = row["relationship"]
    percentile_column = column_name + "_percentile"

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
# %%
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
