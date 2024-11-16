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
def recalculate_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


# %%

# ____________________________________________________________________________________
# Config
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20240609_tunedparams"
plot_sigs_config_path = "plot_sigs_config.csv"
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

fig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\AGU24"  # os.path.join(out_dir, "figs")
# if not os.path.exists(fig_dir):
#     os.makedirs(fig_dir)
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
    os.path.join(out_dir, "out_calc_All_custom_filt.csv"), index_col="gauge_id"
)
# _df_sigs = _df_sigs.join(attrs_caravan, how="left")
df_sigs = _df_sigs.join(eco_caravan, how="left")

# %%
# Get the percentile
for sigs_name in plot_sigs_config["column_name"]:
    # Get df[sigs_name]
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    df_sigs[sigs_name + "_percentile"] = column_data.rank(pct=True) * 100


# %% ________________________________________________
def plot_sig_map(df, sig_name, overlay_layer, mode="normal", filetype="png"):

    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add a legend
    # overlay_layer.plot(
    #     ax=ax,
    #     edgecolor="white",
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
        out_file_name = f"map_{sig_name}.{filetype}"
        title_label = f"{plot_config["label"]}"
    elif mode == "percentile":
        plot_config = plot_sigs_config.loc[
            plot_sigs_config["column_name"] == sig_name
        ].iloc[0]
        c_data = df[sig_name + "_percentile"]
        llim = 0
        ulim = 100
        cbar_label = "percentile"
        out_file_name = f"map_perc_{sig_name}.{filetype}"
        title_label = f"{plot_config["label"]}"
    elif mode == "process_perc":
        c_data = df[sig_name + "_medperc"]
        llim = 0
        ulim = 100
        cbar_label = "Median percentile"
        out_file_name = f"map_medperc_{sig_name}.{filetype}"
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
    cbar = plt.colorbar(scatter, ax=ax, orientation="horizontal", shrink=0.5)
    cbar.set_label("Colorbar Label", labelpad=10)
    # cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
    # cbar.set_label(cbar_label, rotation=270, labelpad=30)
    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, out_file_name))


# %%
# ______________________________________________________________________________
# Plot the average percentile per processes
# process_name = "Baseflow"
# process_name = "Saturation Excess Overlandflow"
process_name = "Infiltration Excess Overlandflow"
# process_name =  "Water loss to deep GW or ET"# "Storage capacity and retention"  #
# process_name = "ET impacts on storage and baseflow"
process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]

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

# Combine the percentiles and calculate the average
# Do not calculate the median percentile, if there is nan
df_sigs[process_name + "_medperc"] = pd.concat(percentiles, axis=1).median(
    axis=1, skipna=False
)
plot_sig_map(
    df_sigs, process_name, ecoregion_overlay, mode="process_perc", filetype="pdf"
)

# %%
