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
local_dir = r"D:\data"
attr_file = os.path.join(
    cloud_dir,
    "data",
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_gages2_etc_20250517+cluster.csv",
)
gg2_polygon_file = os.path.join(
    cloud_dir,
    "data",
    "GAGES2",
    "GAGES_II_Geospa",
    "all_gages2_polygons.shp",
)
camels_polygon_file = os.path.join(
    local_dir,
    "Caravan1.4",
    "shapefiles",
    "camels",
    "camels_basin_shapes.shp",
)
hysets_polygon_file = os.path.join(
    local_dir,
    "Caravan1.4",
    "shapefiles",
    "hysets",
    "hysets_basin_shapes.shp",
)
sfig_dir = os.path.join(cloud_dir, "figs", "supfig_attrs_and_shap")
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

if not os.path.exists(sfig_dir):
    os.makedirs(sfig_dir)


# %%
# ____________________________________________________________________________________
# load attrs

# Load attributes
attrs = pd.read_csv(attr_file, index_col="gauge_id")
attrs["usgs_gauge_id"] = attrs["usgs_gauge_id"].astype(str).str.zfill(8)
attrs["usgs_gauge_id"].head()
# %%
# Load watershed shapefiles
gg2_polygon = gpd.read_file(gg2_polygon_file).to_crs(epsg=4326)
gg2_polygon["gauge_id"] = "gages2_" + gg2_polygon["GAGE_ID"].astype(str).str.zfill(8)
# %%
gg2_polygon["gauge_num"] = gg2_polygon["GAGE_ID"].astype(str).str.zfill(8)
# %%
camels_polygon = gpd.read_file(camels_polygon_file).to_crs(epsg=4326)
camels_polygon["gauge_num"] = (
    camels_polygon["gauge_id"]
    .str.split("_")
    .str[1]
    .astype(int)
    .astype(str)
    .str.zfill(8)
)
# %%
hysets_polygon = gpd.read_file(hysets_polygon_file).to_crs(epsg=4326)
hysets_polygon["gauge_num"] = (
    hysets_polygon["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)
# %%
col_sel = ["gauge_num", "gauge_id", "geometry"]
_polygons = pd.concat(
    [gg2_polygon[col_sel], camels_polygon[col_sel], hysets_polygon[col_sel]],
    ignore_index=True,
)
polygons = _polygons.drop_duplicates(subset=["gauge_num"], keep="first")
polygons.head()
print(len(polygons))
# %%
attrs = attrs.merge(
    polygons,
    left_on="usgs_gauge_id",
    right_on="gauge_num",
    suffixes=("", "_polygons"),
    how="left",
)
# %%
attrs.set_index("gauge_id", inplace=True)
# %%
attrs.head()

# %%
attrs["area"] = attrs["geometry"].values.area
attrs = gpd.GeoDataFrame(attrs, geometry="geometry")
# %%
print(len(attrs))


# %%
from matplotlib.colors import Normalize, LogNorm
from matplotlib.cm import ScalarMappable


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

    df.sort_values(by="area", ascending=False, inplace=True)

    # Plot the max category per location
    df.dropna(subset=[attr_name], inplace=True)

    # Define the bounds of the attribute
    bound_dict = {
        "P_mm_day": (0, 5),
        "PET_mm_day": (0, 4),
        "ARIDITY_GAGES2": (0, 2),
        "seasonality_FAO_PM": (0, 2),
        "low_prec_freq": (0.6, 1.0),
        "SNOW_FRAC_PRECIP": (0, 0.5),
        "ELEV_MEAN_M_BASIN": (0, 2000),
        "SLOPE_DEG_x10": (1e-16, 50),
        "CLAYAVE": (0, 50),
        "SILTAVE": (0, 70),
        "geol_weighted_ave_age_ma": (0, 2500),
        "kar_pc_sse": (0, 70),
        "FORESTNLCD06": (0, 60),
        "CROPSNLCD06": (0, 60),
        "PDEN_2000_BLOCK": (0, 500),
        "T_AVG_BASIN": (0, 20),
        "ROCKDEPAVE": (20, 60),
        "WTDEPAVE": (0, 7),
        "CROPSNLCD06": (0, 60),
        "PCT_IRRIG_AG": (0, 10),
    }

    vmin = bound_dict[attr_name][0]
    vmax = bound_dict[attr_name][1]
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap("YlGnBu")
    sm = ScalarMappable(norm=norm, cmap=cmap)
    df.plot(
        ax=ax,
        column=attr_name,
        cmap=cmap,
        norm=norm,
        alpha=0.5,
        zorder=99,
    )

    # Dictionary mapping attribute names to their units
    unit_dict = {
        "P_mm_day": "mm/day",
        "PET_mm_day": "mm/day",
        "ARIDITY_GAGES2": "-",
        "seasonality_FAO_PM": "-",
        "low_prec_freq": "-",
        "SNOW_FRAC_PRECIP": "-",
        "ELEV_MEAN_M_BASIN": "m",
        "SLOPE_DEG_x10": "deg×10",
        "CLAYAVE": r"%",
        "SILTAVE": r"%",
        "geol_weighted_ave_age_ma": "Ma",
        "kar_pc_sse": r"%area",
        "FORESTNLCD06": r"%area",
        "PDEN_2000_BLOCK": r"ppl/$km^2$",
        "T_AVG_BASIN": "°C",
        "ROCKDEPAVE": "inches",
        "WTDEPAVE": "feet",
        "CROPSNLCD06": r"%area",
        "PCT_IRRIG_AG": r"%area",
    }

    # Add a colorbar in bottom right corner
    cax = fig.add_axes([0.85, 0.15, 0.02, 0.2])  # [left, bottom, width, height]
    cbar = plt.colorbar(sm, cax=cax)
    unit = unit_dict.get(attr_name, "")
    cbar.set_label(f"[{unit}]", fontsize=12)
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


# attr_names = [
#     "P_mm_day",
#     "PET_mm_day",
#     "ARIDITY_GAGES2",
#     "seasonality_FAO_PM",
#     "low_prec_freq",
#     "SNOW_FRAC_PRECIP",
#     "ELEV_MEAN_M_BASIN",
#     "SLOPE_DEG_x10",
#     "CLAYAVE",
#     "SILTAVE",
#     "geol_weighted_ave_age_ma",
#     "kar_pc_sse",
#     "FORESTNLCD06",
#     "PDEN_2000_BLOCK",
# ]
attr_names = [
    # "T_AVG_BASIN",
    # "ROCKDEPAVE",
    # "WTDEPAVE",
    # "CROPSNLCD06",
    "PCT_IRRIG_AG",
]
for attr_name in attr_names:
    plot_attrs_in_map(
        attrs,
        attr_name=attr_name,
        file_type="png",
    )

# %%
attrs["PCT_IRRIG_AG"].hist(bins=100)
# %%
