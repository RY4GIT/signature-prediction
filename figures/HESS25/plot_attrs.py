# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import patches
import geopandas as gpd

# %%
########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
rf_out_dir = os.path.join(rf_dir, "output_raraki_20250826_cluster_all")
rf_out_dir_Wu = os.path.join(rf_dir, "output_raraki_20250827_cluster_all_Wu")
fig_dir = os.path.join(cloud_dir, "figs", "fig_varImp")
sfig_dir = os.path.join(cloud_dir, "figs", "supfig_attrs_and_shap")
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)
if not os.path.exists(sfig_dir):
    os.makedirs(sfig_dir)

# ____________________________________________________________________________________
# Plot configs

# Attributes info & colors
config_attrs_info_file = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_attrs_info.csv"
)
attrs_info = pd.read_csv(config_attrs_info_file)
with open(
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_attrs_colors_high_contrast.json",
    "r",
) as file:
    attrs_colors = json.load(file)

# Signature info
sigs_RF_names_ordered = [
    "BFI",
    "BaseflowRecessionK",
    "AverageStorage",
    "RecessionParameters_b",
    "TotalRR",
    "EventRR",
    "Recession_a_Seasonality",
    "VariabilityIndex",
    "IE_thresh",
    "IE_thresh_signif",
    "SE_thresh",
    "SE_thresh_signif",
    "R_Pint_RC",
    "R_Pvol_RC",
]
sig_Wu_names = [
    "R_Pint_RC",
    "R_Pvol_RC",
]


# %%
# ____________________________________________________________________________________
# load CAMELS and HYSETS attributes

caravan_attrs_dir = r"D:\data\Caravan1.4\attributes"
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

attrs_camels = pd.read_csv(attrs_camels_file)
attrs_hysets = pd.read_csv(attrs_hysets_file)
attrs_camels["gauge_id"] = attrs_camels["gauge_id"].astype(str)
attrs_hysets["gauge_id"] = attrs_hysets["gauge_id"].astype(str)

# %%
print("Loading Caravan watershed shapefiles...")


# cARAVAN 1.5 shapefile is somehow corrupted, so use Caravan 1.4
local_dir = r"D:\data"
wspolygon_camels_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "camels", "camels_basin_shapes.shp"
)
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "hysets", "hysets_basin_shapes.shp"
)
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets]).set_index("gauge_id")

# %%


def plot_attrs_in_map(
    df,
    attr_name,
    file_type="png",
):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add the BORDERS feature first
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

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
        facecolor="#c3c4c8",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=1.0,  # Optionally adjust linewidth for edges
    )

    # # Add state boundary lines beneath data
    # ax.add_feature(
    #     cfeature.STATES,
    #     edgecolor="#9e9e9e",
    #     linewidth=0.75,
    # )

    df["area"] = df["geometry"].area
    df.sort_values(by="area", ascending=False, inplace=True)

    # Plot the max category per location
    df.dropna(subset=[attr_name], inplace=True)

    vabs = np.mean(
        [np.abs(df[attr_name].quantile(0.10)), np.abs(df[attr_name].quantile(0.90))]
    )
    vmin = vabs * -1
    vmax = vabs
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap("viridis")
    sm = ScalarMappable(norm=norm, cmap=cmap)
    df.plot(
        ax=ax,
        column=attr_name,
        cmap=cmap,
        norm=norm,
        alpha=0.5,
        zorder=99,
    )

    # Add a colorbar in bottom right corner
    cax = fig.add_axes([0.85, 0.15, 0.02, 0.2])  # [left, bottom, width, height]
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label(attr_name, fontsize=12)
    cbar.ax.tick_params(labelsize=12)

    # Save plot
    file_name = f"attrs_{attr_name}.{file_type}"

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    ax.set_title(attr_name, fontsize=18, loc="left")
    # ax.set_extent(conus_extent)

    # Set spines invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    fig.savefig(
        os.path.join(sfig_dir, file_name),
        dpi=300,
        bbox_inches="tight",
    )


attr_names = [
    "P_mm_day",
    "PET_mm_day",
    "ARIDITY_GAGES2",
    "seasonality_FAO_PM",
    "low_prec_freq",
    "SNOW_FRAC_PRECIP",
    "ELEV_MEAN_M_BASIN",
    "SLOPE_DEG_x10",
    "CLAYAVE",
    "SILTAVE",
    "geol_weighted_ave_age_ma",
    "kar_pc_sse",
    "FORESTNLCD06",
    "PDEN_2000_BLOCK",
]
for attr_name in attr_names:
    df_subset = df_shap_with_attrs[(df_shap_with_attrs["feature"] == attr_name)].copy()

    # Concatenate the dataframes and add the polygon data
    print("Original length of wspolygon: ", len(wspolygon))
    print("Original length of df_subset: ", len(df_subset))
    df_subset = wspolygon.join(
        df_subset.set_index("gauge_id"), how="right"
    ).reset_index()
    print("Length of df_subset: ", len(df_subset))

    plot_shap_in_map(
        df_subset,
        sig_name=sig_name,
        attr_name=attr_name,
        varname="phi",
        file_type="png",
    )
