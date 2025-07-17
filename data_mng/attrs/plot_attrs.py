# %%
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# %%
# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
data_dir = r"D:\data"

print("Loading Attributes file...")
cara_file_path = os.path.join(
    cloud_dir,
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_gages2_etc_20250517+cluster.csv",
)
cara_attrs = pd.read_csv(cara_file_path)
print("Loading Caravan watershed shapefiles...")
caravan_shp_dir = os.path.join(data_dir, "Caravan1.4", "shapefiles")
camels_polygon_file = os.path.join(caravan_shp_dir, "camels", "camels_basin_shapes.shp")
camels_polygon = gpd.read_file(camels_polygon_file).to_crs(epsg=4326)
hysets_polygon_file = os.path.join(caravan_shp_dir, "hysets", "hysets_basin_shapes.shp")
hysets_polygon = gpd.read_file(hysets_polygon_file).to_crs(epsg=4326)
cara_polygons = pd.concat([camels_polygon, hysets_polygon], ignore_index=True)

cara_polygons = cara_polygons.join(
    cara_attrs.set_index("gauge_id"), on="gauge_id", rsuffix="_attrs"
)
cara_polygons = cara_polygons[cara_polygons["country"] == "United States of America"]
cara_polygons.sort_values("area", ascending=False, inplace=True)
cara_polygons["usgs_gauge_id"] = cara_polygons["gauge_id"].apply(
    lambda x: x.split("_")[1]
)
cara_polygons.set_index("gauge_id", inplace=True)


# %% #########################################################################
#
# PLOT ATTRIBUTES
#
##############################################################################

out_dir = os.path.join(data_dir, "derived_attrs", "assembled_RA", "figs", "attr_plots")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

attr_names = [
    "ELEV_MEAN_M_BASIN",
    "DRAIN_SQKM",
    "SLOPE_DEG_x10",
    "FORESTNLCD06",
    "CROPSNLCD06",
    "PASTURENLCD06",
    "PCT_IRRIG_AG",
    "PADCAT1_AND_2",
    "isowet_areafrac",
    "CLAYAVE",
    "SILTAVE",
    "soc_th_sav",
    "kar_pc_sse",
    "geol_weighted_ave_age_ma",
    "PDEN_2000_BLOCK",
    "P_mm_day",
    "PET_mm_day",
    "ARIDITY_GAGES2",
    "SNOW_FRAC_PRECIP",
    "seasonality_FAO_PM",
    "high_prec_freq",
    "low_prec_freq",
    "low_prec_dur",
]
# attr_names = [
#     "ELEV_MEAN_M_BASIN",
#     "DRAIN_SQKM",
#     "SLOPE_PCT",
#     "FORESTNLCD06",
#     "CROPSNLCD06",
#     "PASTURENLCD06",
#     "PCT_IRRIG_AG",
#     "SNOWICENLCD06",
#     "PADCAT1_AND_2",
#     "isowet_areafrac",
#     "CLAYAVE",
#     "SILTAVE",
#     "OMAVE",
#     "kar_pc_sse",
#     "geol_weighted_ave_age_ma",
#     "PDEN_2000_BLOCK",
#     "gdp_ud_sav",
#     "FRAGUN_BASIN",
#     "P_mm_day",
#     "PET_mm_day",
#     "ARIDITY_GAGES2",
#     "SNOW_PCT_PRECIP",
#     "PRECIP_SEAS_IND",
#     "high_prec_freq",
#     "low_prec_freq",
#     "low_prec_dur",
#     "PERDUN",
#     "PERHOR",
#     "TOPWET",
#     "HIRES_LENTIC_DENS",
#     "PADCAT1_PCT_BASIN",
#     "PADCAT2_PCT_BASIN",
#     "PADCAT3_PCT_BASIN",
#     "ASPECT_NORTHNESS",
#     "ASPECT_EASTNESS",
#     "BAS_COMPACTNESS",
#     "RH_BASIN",
#     "T_AVG_BASIN",
#     "WD_BASIN",
#     "STREAMS_KM_SQ_KM",
#     "MAINSTEM_SINUOUSITY",
#     "ARTIFPATH_PCT",
#     "ARTIFPATH_MAINSTEM_PCT",
#     "PCT_1ST_ORDER",
#     "PCT_6TH_ORDER_OR_MORE",
#     "PCT_NO_ORDER",
#     "CANALS_PCT",
#     "CANALS_MAINSTEM_PCT",
#     "FRESHW_WITHDRAWAL",
#     "FRAGUN_BASIN",
#     "HIRES_LENTIC_DENS",
#     "HIRES_LENTIC_MEANSIZ",
#     "DEVNLCD06",
#     "PLANTNLCD06",
#     "WATERNLCD06",
#     "BARRENNLCD06",
#     "DECIDNLCD06",
#     "EVERGRNLCD06",
#     "MIXEDFORNLCD06",
#     "SHRUBNLCD06",
#     "GRASSNLCD06",
#     "WOODYWETNLCD06",
#     "EMERGWETNLCD06",
#     "HGA",
#     "HGB",
#     "HGAD",
#     "HGC",
#     "HGD",
#     "HGAC",
#     "HGBD",
#     "HGCD",
#     "HGBC",
#     "HGVAR",
#     "WTDEPAVE",
#     "ROCKDEPAVE",
#     "SANDAVE",
#     "RRMEAN",
#     "input_seasonality",
#     "input_PET_synchrony",
# ]

land = cfeature.NaturalEarthFeature(
    "physical",
    "land",
    "50m",
    edgecolor="face",
    facecolor="lightgray",  # Set land color to light gray
)
states = cfeature.NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_lines",
    edgecolor="white",
)
# Use log scale normalization for population density
from matplotlib.colors import LogNorm

for attr_name in attr_names:
    try:
        print(f"Plotting {attr_name}...")

        # Set up the map
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        ax.add_feature(land)
        ax.add_feature(states, linewidth=0.5)  # , linestyle=":", alpha=0.5)

        # Set extent to CONUS
        ax.set_extent([-124.85, -66.95, 24.396308, 49.384358])

        # Add map features
        ax.add_feature(cfeature.COASTLINE, color="white")  # Set coastline color to grey
        ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")
        # ax.add_feature(cfeature.STATES, linestyle=":", color="white")

        # Create a colorbar using the normalization and colormap from the plot
        vmin = cara_polygons[attr_name].quantile(0.10)
        vmax = cara_polygons[attr_name].quantile(0.90)
        cmap = "YlGnBu"

        if attr_name in ["PERHOR"]:
            vmin = vmin
            vmax = vmax
            norm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            norm = Normalize(vmin=vmin, vmax=vmax)

        # Create colormap and scalar mappable
        cmap = plt.get_cmap(name=cmap)
        sm = ScalarMappable(norm=norm, cmap=cmap)

        # Plot the data
        sheds = cara_polygons.plot(
            ax=ax,
            column=attr_name,
            cmap=cmap,
            norm=norm,
            alpha=0.7,
            edgecolor="white",
            linewidth=0.3,
            legend=False,
            zorder=99,
        )

        # Add colorbar
        cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label(attr_name)

        # Add a title
        ax.set_title(attr_name)

        # Display the plot
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{attr_name}.png"))
    except Exception as e:
        print(f"Error plotting {attr_name}: {e}")
        continue


# %%
