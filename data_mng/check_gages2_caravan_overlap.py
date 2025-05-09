# %% Script to check the overlap between GAGES2 and Caravan watersheds
import os
import glob
import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"

print("Loading Attributes file...")
cara_file_path = os.path.join(
    data_dir,
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_and_gages2+climate+morph+padcat.csv",
)
cara_attrs = pd.read_csv(cara_file_path)

gages2_file_path = os.path.join(
    data_dir,
    "GAGES2",
    "GAGES_II_attrs",
    "gagesII_sept30_2011_concat.csv",
)
gages2_all = pd.read_csv(gages2_file_path)

# #########################################################################
#
# LOAD SIGNATURES
#
##############################################################################
print("Loading Signature file...")
# Signature output path after quality control
sig_file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20250223_withWu\out_calc_All_custom_filt_qc_snow_area.csv"
sigs = pd.read_csv(sig_file_path)

# #########################################################################
#
# LOAD SHAPEFILES
#
##############################################################################
print("Loading Caravan watershed shapefiles...")
caravan_shp_dir = os.path.join(data_dir, "Caravan1.4", "shapefiles")
camels_polygon_file = os.path.join(caravan_shp_dir, "camels", "camels_basin_shapes.shp")
camels_polygon = gpd.read_file(camels_polygon_file).to_crs(epsg=4326)
hysets_polygon_file = os.path.join(caravan_shp_dir, "hysets", "hysets_basin_shapes.shp")
hysets_polygon = gpd.read_file(hysets_polygon_file).to_crs(epsg=4326)
cara_polygons = pd.concat([camels_polygon, hysets_polygon], ignore_index=True)
# %%
cara_polygons = cara_polygons.join(
    cara_attrs.set_index("gauge_id"), on="gauge_id", rsuffix="_attrs"
)
cara_polygons = cara_polygons[cara_polygons["country"] == "United States of America"]
cara_polygons["usgs_gauge_id"] = cara_polygons["gauge_id"].apply(
    lambda x: x.split("_")[1]
)
cara_polygons.set_index("gauge_id", inplace=True)

# %%
print("Loading GAGES-II watershed shapefiles...")
gages2_shp_dir = output_shapefile_path = os.path.join(
    data_dir, "GAGES2", "GAGES_II_Geospa", "gages2_polygons.shp"
)
gages2_polygons = gpd.read_file(gages2_shp_dir).to_crs(epsg=4326)

# %% #########################################################################
#
# COMPARE GAGES2 AND CARAVAN SAMPLES (REF VS NON-REF)
#
##############################################################################
cara_attrs["usgs_gauge_id"] = cara_attrs["gauge_id"].apply(lambda x: x.split("_")[1])
cara_attrs["usgs_gauge_id"]

caravan_area_name = "area"
gages2_area_name = "DRAIN_SQKM"

caravan_all = cara_attrs[cara_attrs[caravan_area_name].notna()].copy()
gages2_subset = cara_attrs[cara_attrs[gages2_area_name].notna()].copy()

caravan_gages_overlap = caravan_all.merge(
    gages2_subset, how="inner", left_on="gauge_id", right_on="gauge_id"
)

caravan_gages_nonoverlap = caravan_all[
    ~caravan_all["gauge_id"].isin(caravan_gages_overlap["gauge_id"])
].copy()

gages_caravan_nonoverlap = gages2_all[
    ~gages2_all["usgs_gauge_id"].isin(cara_attrs["usgs_gauge_id"])
].copy()

caravan_nsample = caravan_all.shape[0]
caravan_ref_nsample = caravan_all[caravan_all["CLASS"] == "Ref"].shape[0]
caravan_nonref_nsample = caravan_nsample - caravan_ref_nsample
gages2_nsample = gages2_subset.shape[0]
gages2_ref_nsample = gages2_subset[gages2_subset["CLASS"] == "Ref"].shape[0]
gages2_nonref_nsample = gages2_subset[gages2_subset["CLASS"] == "Non-ref"].shape[0]
caravan_gages2_overlap_nsample = caravan_gages_overlap.shape[0]
caravan_gages2_nonoverlap_nsample = caravan_gages_nonoverlap.shape[0]
gages2_caravan_nonoverlap_nsample = gages_caravan_nonoverlap.shape[0]
print(f"Caravan all: {caravan_nsample}")
print(
    f"Caravan, GAGES-II ref gauges: {caravan_ref_nsample} ({caravan_ref_nsample / caravan_nsample * 100:.1f}%)"
)
print(
    f"Caravan, GAGES-II non-ref gauges: {caravan_nonref_nsample} ({caravan_nonref_nsample / caravan_nsample * 100:.1f}%)"
)
print(
    f"GAGES2 subset: {gages2_nsample} ({caravan_gages2_overlap_nsample / caravan_nsample * 100:.1f}% of Caravan)"
)
print(
    f"GAGES2 subset, ref gauges: {gages2_ref_nsample} ({gages2_ref_nsample / gages2_nsample * 100:.1f}%)"
)
print(
    f"GAGES2 subset, non-ref gauges: {gages2_nonref_nsample} ({gages2_nonref_nsample / gages2_nsample * 100:.1f}%)"
)
print(
    f"Caravan-GAGES2 overlap: {caravan_gages2_overlap_nsample} (this should match with GAGES2 subset)"
)
print("In Caravan but not in GAGES2: ", caravan_gages2_nonoverlap_nsample)
print("In GAGES2 but not in Caravan: ", gages2_caravan_nonoverlap_nsample)

print(
    f"Signatures were calculated for: {len(sigs)} watersheds ({len(sigs) / caravan_nsample * 100:.1f}% of Caravan)"
)
print(
    f"Signatures were NOT calculated for: {caravan_nsample - len(sigs)} watersheds ({(caravan_nsample - len(sigs)) / caravan_nsample * 100:.1f}% of Caravan)"
)

# %% #########################################################################
#
# CHECK THE SPATIAL DISTRIBUTION OF EXCLUDED WATERSHEDS
#
##############################################################################

# GAGES2, not within Caravan
# - Signatures from this watershed can be potentially predicted
# - by pulling Caravan attributes and using the existing GAGES-II att ributes


# %%
# Within Caravan, excluded because of data quality (>30% NaN, <5yrs)
# But still excluding the snowy watersheds, with bad area estimates
# - Signatures from this watershed can be potentially predicted
# - For those overlapping with GAGES2, we can use the existing GAGES-II attributes
# - For those not overlapping with GAGES2, we can replace with the existing Caravan attributes


# %% #########################################################################
#
# CHECK THE SPATIAL DISTRIBUTION OF EXCLUDED WATERSHEDS
#
##############################################################################


def plot_watershed_categories(cara_polygons, gages2_polygons, sigs):
    """
    Plot watersheds with different colors based on their availability in datasets:
    - Light grey: Caravan watersheds where signatures are observed
    - Orange: Caravan watersheds without signatures but present in GAGES-II
    - Red: Caravan watersheds without signatures and not in GAGES-II
    - Blue: GAGES-II watersheds not in Caravan
    """
    # Set up the figure and axis
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add base map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=":", linewidth=0.5)
    ax.add_feature(cfeature.STATES, linestyle="-", linewidth=0.2, edgecolor="gray")

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 50.5], crs=ccrs.PlateCarree())

    # Sort by area so that it appears nice in the map
    cara_polygons = cara_polygons.sort_values(by="area")
    gages2_polygons = gages2_polygons.sort_values(by="AREA")

    # Get the different categories of watersheds

    # 1. Caravan watersheds with signatures (light grey)
    print("Plotting Caravan watersheds with signatures...")
    sig_gauge_ids = set(sigs["gauge_id"])
    cara_with_sigs = cara_polygons.loc[
        cara_polygons.index.intersection(sig_gauge_ids)
    ].copy()

    cara_with_sigs.plot(
        ax=ax,
        color="lightgrey",
        alpha=0.6,
        label="Caravan (sig - obs)",
        edgecolor="white",
        linewidth=0.3,
    )

    # 2. Caravan watersheds without signatures but in GAGES-II (orange)
    print("Plotting Caravan watersheds without signatures but in GAGES-II...")
    cara_without_sigs = cara_polygons.loc[
        ~cara_polygons.index.isin(sig_gauge_ids)
    ].copy()
    gages2_gauge_ids = set(gages2_polygons["GAGE_ID"])
    cara_in_gages2 = cara_without_sigs[
        cara_without_sigs["usgs_gauge_id"].isin(gages2_gauge_ids)
    ].copy()
    cara_in_gages2.plot(
        ax=ax,
        color="tab:orange",
        alpha=0.3,
        label="Cara/gages2 - pred",
        edgecolor="white",
        linewidth=0.3,
    )

    # 3. Caravan watersheds without signatures and not in GAGES-II (red)
    print("Plotting Caravan watersheds without signatures and not in GAGES-II...")
    cara_not_in_gages2 = cara_without_sigs[
        ~cara_without_sigs["usgs_gauge_id"].isin(gages2_gauge_ids)
    ].copy()
    cara_not_in_gages2.plot(
        ax=ax,
        color="tab:red",
        alpha=0.3,
        label="Cara - pred",
        edgecolor="white",
        linewidth=0.3,
    )

    # 4. GAGES-II watersheds not in Caravan (blue)
    print("Plotting GAGES-II watersheds not in Caravan...")
    caravan_usgs_ids = set(cara_polygons["usgs_gauge_id"])
    sig_usgs_ids = set(sigs["gauge_id"].apply(lambda x: x.split("_")[1]))
    gages2_not_in_cara = gages2_polygons[
        ~(
            gages2_polygons["GAGE_ID"].isin(caravan_usgs_ids)
            | gages2_polygons["GAGE_ID"].isin(sig_usgs_ids)
        )
    ].copy()
    gages2_not_in_cara.plot(
        ax=ax,
        color="tab:blue",
        alpha=0.3,
        label="Gages2 - pred",
        edgecolor="white",
        linewidth=0.3,
    )

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="lightgrey",
            label=f"Caravan (sig - observation available) \n {len(cara_with_sigs)}",
            markerfacecolor="lightgrey",
            markersize=10,
            linestyle="None",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="tab:orange",
            label=f"Cara/gages2 - can be predicted easily \n {len(cara_in_gages2)}",
            markerfacecolor="tab:orange",
            markersize=10,
            linestyle="None",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="tab:red",
            label=f"Cara - can be predicted only with HydroAtlas attrs \n {len(cara_not_in_gages2)}",
            markerfacecolor="tab:red",
            markersize=10,
            linestyle="None",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="tab:blue",
            label=f"Gages2 - can be predicted by pulling Caravan attrs \n {len(gages2_not_in_cara)}",
            markerfacecolor="tab:blue",
            markersize=10,
            linestyle="None",
        ),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=12)

    plt.tight_layout()
    print("Saving figure...")
    plt.savefig(
        os.path.join(
            data_dir,
            "derived_attrs",
            "assembled_RA",
            "figs",
            "watershed_overlap.pdf",
        ),
        dpi=300,
        bbox_inches="tight",
    )
    # plt.show()
    print("Figure saved.")
    return fig, ax


# Call the function
fig, ax = plot_watershed_categories(cara_polygons, gages2_polygons, sigs)


# %%
# # %%
# # Check the number of samples for each class in the Caravan-GAGES2 overlap
# # %%
# prancevic_subset = attrs[
#     attrs["p99_pave"].notna() & attrs[gages2_attr_name].notna()
# ].copy()
# prancevic_subset_nsample = prancevic_subset.shape[0]
# prancevic_subset_ref_nsample = prancevic_subset[
#     prancevic_subset["CLASS"] == "Ref"
# ].shape[0]
# prancevic_subset_nonref_nsample = (
#     prancevic_subset_nsample - prancevic_subset_ref_nsample
# )

# print(f"Prancevic & GAGES2 subset: {prancevic_subset_nsample}")
# print(
#     f"Prancevic & GAGES2 ref gauges:{prancevic_subset_ref_nsample} ({prancevic_subset_ref_nsample / prancevic_subset_nsample * 100:.1f}%)"
# )
# print(
#     f"Prancevic & GAGES2 non-ref gauges:{prancevic_subset_nonref_nsample} ({prancevic_subset_nonref_nsample / prancevic_subset_nsample * 100:.1f}%)"
# )


# # %%
# def plot_hist(df, attr_name, title, bins=200, ax=None, xlim=None):
#     if ax is None:
#         fig, ax = plt.subplots(figsize=(6, 4))
#     df[attr_name][df["CLASS"] == "Ref"].hist(
#         bins=bins, color="tab:blue", label="Ref", alpha=0.5, ax=ax
#     )
#     df[attr_name][df["CLASS"] != "Ref"].hist(
#         bins=bins, color="tab:pink", label="Non-ref", alpha=0.5, ax=ax
#     )
#     ax.set_title(title)
#     ax.set_xlabel(attr_name)
#     ax.set_ylabel("Frequency")
#     ax.legend()
#     if xlim:
#         ax.set_xlim(xlim)


# # HYDRO_DISTURB_INDX	- Hydrologic "disturbance index" score,
# # based on 7 variables: 1) MAJ_DDENS_2009, 2) WATER_WITHDR,
# # 3) change in dam storage 1950-2009, 4) CANALS_PCT,
# # 5) RAW_DIS_NEAREST_MAJ_NPDES, 6) ROADS_KM_SQ_KM, and 7) FRAGUN_BASIN.
# # Low values = low anthropogenic hydrologic modification
# # Plot histograms as a 1-by-2 subplot for specific attributes

# # Plot histograms as a 1-by-2 subplot for specific attributes
# attr_anthro_caravan = ["ppd_pk_sav", "gdp_ud_sav", "hdi_ix_sav"]
# for attr in attr_anthro_caravan:
#     fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
#     if attr == "gdp_ud_sav" or attr == "ppd_pk_sav":
#         xlim = (caravan_all[attr].quantile(0.10), caravan_all[attr].quantile(0.90))
#     else:
#         xlim = None
#     plot_hist(caravan_all, attr, f"Caravan ALL - {attr}", ax=axes[0], xlim=xlim)
#     plot_hist(
#         gages2_subset, attr, f"Caravan-GAGES2 subset - {attr}", ax=axes[1], xlim=xlim
#     )
#     plt.tight_layout()
#     plt.show()

# # Plot single histograms for other attributes
# attr_anthro_gages2 = [
#     "MAJ_DDENS_2009",
#     "CANALS_PCT",
#     "RAW_DIS_NEAREST_MAJ_NPDES",
#     "ROADS_KM_SQ_KM",
#     "FRAGUN_BASIN",
# ]
# for attr in attr_anthro_gages2:
#     if attr == "RAW_DIS_NEAREST_MAJ_NPDES":
#         xlim = (0, 200)
#     elif attr == "MAJ_DDENS_2009" or attr == "CANALS_PCT":
#         xlim = (caravan_all[attr].quantile(0.10), caravan_all[attr].quantile(0.90))
#     else:
#         xlim = None
#     plot_hist(gages2_subset, attr, f"Caravan-GAGES2 subset - {attr}", xlim=xlim)
