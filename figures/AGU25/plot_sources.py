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
    "fig_sources",
)
# Plotting config
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_sigs.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# Drop Wu signatures from the plot_sigs_config
plot_sigs_config = plot_sigs_config[
    ~plot_sigs_config["column_name"].isin(
        ["R_Pint_RC", "R_Pvol_RC", "diff_RCPint_RCPvol"]
    )
]

# Make Figure directory
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# Conus extent
conus_extent = [-125.5, -66.95, 24.396308, 47.5]

# # %%
# # ____________________________________________________________________________________
# # Load overlay layer for plotting
# print("Loading overlay layer...")
# # Ecoregion overlay
# _ecoregion_overlay = gpd.read_file(
#     os.path.join(gdrive_dir, "data", "EcoRegions", "NA_CEC_Eco_Level2.shp")
# )
# _ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
# ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
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
        # _df_sigs_rf_overlap_baddata,
        # _df_sigs_rf_hys_only,
        # _df_sigs_rf_gg2_only,
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
# Preprocess the data and count the number of gauges with data
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
# Yes, this line replaces values with NaN for any rows where low_snow is False
# low_snow is True for gauges with snow < threshold, False otherwise
# So ~low_snow is True for gauges with high snow, which get masked to NaN
df_sigs[mask_cols] = df_sigs[mask_cols].mask(~low_snow)

print(
    f"{df_sigs['IE_thresh'].isna().sum()} gauges ({df_sigs['IE_thresh'].isna().sum() / len(df_sigs) * 100:.1f}%) have snow data above {frac_snow_thresh * 100}%"
)
# %%
print("Data length: ", len(df_sigs))
print("Baseflow data length: ", len(df_sigs[df_sigs["BFI"].notna()]))
print("Overlandflow data length: ", len(df_sigs[df_sigs["IE_thresh"].notna()]))
print("Number of gauges by data source:")
# %%
print(df_sigs.dropna(subset=["BFI"]).groupby("source").size())
print(df_sigs.dropna(subset=["TotalRR"]).groupby("source").size())

# %%
#######################################################
# Plot the source
#######################################################

# Define source colors
source_colors = {
    "Caravan_obs": {"color": "lightgrey", "label": "Caravan (Observed)", "alpha": 0.4},
    "GAGES2_obs": {"color": "tab:blue", "label": "GAGES-II (Observed)", "alpha": 0.7},
    # "RF_overlap_baddata": {
    #     "color": "tab:red",
    #     "label": "RF (Caravan+GAGES-II\noverlap)",
    #     "alpha": 0.7,
    # },
    # "RF_hys_only": {"color": "tab:orange", "label": "RF (Caravan only)", "alpha": 0.7},
    # "RF_gg2_only": {"color": "#F0E442", "label": "RF (GAGES-II only)", "alpha": 0.7},
}


def plot_source(df):  # , overlay_layer):
    # Get plot config

    # Set up the map
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # # Add a legend
    # overlay_layer.plot(
    #     ax=ax,
    #     edgecolor="grey",
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

    # Add map features
    # ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, color="grey")

    # Add state boundary lines beneath data
    ax.add_feature(
        cfeature.STATES,
        edgecolor="grey",
        linewidth=0.3,
        zorder=100,
    )

    # Create legend patches
    legend_patches = []
    for source in [
        # "RF_gg2_only",
        # "RF_hys_only",
        # "RF_overlap_baddata",
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
    plt.savefig(os.path.join(fig_dir, "fig_sources_agu25_obs.png"), dpi=300)


plot_source(df_sigs)  # , ecoregion_overlay)

# %%
