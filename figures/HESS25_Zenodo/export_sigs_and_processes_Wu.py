# %% Plot Wu 2021 signatures from multiple sources (Caravan, GAGES-II, RF predictions)
import os
import pandas as pd
import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# %% #######################################
# Config
############################################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
sig_dir = os.path.join(cloud_dir, "out", "signatures", "Wu_sigs_20250812")
rf_dir = os.path.join(cloud_dir, "out", "rf", "output_raraki_20250827_cluster_all_Wu")
local_dir = r"D:\data"
fig_dir = os.path.join(
    cloud_dir,
    "figs",
)
zenodo_dir = os.path.join(cloud_dir, "out", "zenodo", "data")
os.makedirs(zenodo_dir, exist_ok=True)

# Plotting config
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_sigs.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# conus_extent = [-125.5, -66.95, 24.396308, 47.5]

# Tolerance in degrees (same order of magnitude as export_sigs_and_processes.py)
_WU_SIMPLIFY_TOL = 0.02


def simplify_geometries(gdf, tolerance=_WU_SIMPLIFY_TOL):
    """Simplify geometries before concat / export to keep GeoJSON size reasonable."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    return gdf


# %% #######################################
# Load datasets
############################################
print("Loading signatures results file ...")


def load_sigs_obs(file_path):
    df_sigs = pd.read_csv(file_path)
    if "gauge_num" in df_sigs.columns:
        df_sigs["gauge_num"] = df_sigs["gauge_num"].astype(str).str.zfill(8)
        df_sigs["gauge_id"] = df_sigs["data_name"] + "_" + df_sigs["gauge_num"]
    else:
        df_sigs["gauge_num"] = df_sigs["gauge_id"].str.split("_").str[1]
    df_sigs.set_index("gauge_id", inplace=True)
    # Pivot long-to-wide if needed: columns become signature names, values are predictions
    if "sig_name" in df_sigs.columns and "prediction" in df_sigs.columns:
        meta_columns = [
            c for c in df_sigs.columns if c not in ["sig_name", "prediction"]
        ]
        meta_per_gauge = df_sigs.groupby(level=0)[meta_columns].first()
        wide_values = df_sigs.pivot_table(
            index=df_sigs.index,
            columns="sig_name",
            values="prediction",
            aggfunc="first",
        )
        wide_values.columns.name = None
        df_sigs = meta_per_gauge.join(wide_values)
    return df_sigs


print("Loading observed signatures results file for Caravan ...")
sigs_obs_cara = load_sigs_obs(
    os.path.join(sig_dir, "out_sigEvent_cara_gg2_rf_train.csv")
)
print(f"Number of Caravan gauges in sigs_obs_cara: {len(sigs_obs_cara)}")
sigs_obs_cara.head()
# %%
print("Loading observed signatures results file for GAGES2 ...")
_sigs_obs_gg2 = load_sigs_obs(
    os.path.join(sig_dir, "out_sigEvent_cara_gg2_no_duplicates.csv")
)
sigs_obs_gg2 = _sigs_obs_gg2[_sigs_obs_gg2["data_name"] == "gages2"].copy()
print(f"Number of GAGES2 gauges in sigs_obs_gg2: {len(sigs_obs_gg2)}")
sigs_obs_gg2.head()
# TDOO:
# %%
print("Loading predicted signatures results files ...")
sigs_pred_gg2 = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_gg2_only_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_gg2: {len(sigs_pred_gg2)}")
sigs_pred_gg2["data_name"] = "pred_gg2"
sigs_pred_gg2.head()
# %%
sigs_pred_hys_gg2 = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_hys_gg2_baddata_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_hys_gg2: {len(sigs_pred_hys_gg2)}")
sigs_pred_hys_gg2["data_name"] = "pred_hys_gg2"
sigs_pred_hys_gg2.head()
# %%
sigs_pred_hys = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_hys_only_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_hys: {len(sigs_pred_hys)}")
sigs_pred_hys["data_name"] = "pred_hys"
sigs_pred_hys.head()


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
    cloud_dir, "data", "GAGES2", "GAGES_II_Geospa", "gages2_polygons_not_cara.shp"
)
gages2_wspolygon = gpd.read_file(gages2_wspolygon_file).to_crs(epsg=4326)
gages2_wspolygon["gauge_id"] = "gages2_" + gages2_wspolygon["GAGE_ID"].astype(
    str
).str.zfill(8)

# %%
print("Simplifying watershed polygons before concat...")
wspolygon_camels = simplify_geometries(wspolygon_camels)
wspolygon_hysets = simplify_geometries(wspolygon_hysets)
gages2_wspolygon = simplify_geometries(gages2_wspolygon)

# %%
print("Loading Caravan attributes...")
cara_attrs_path = os.path.join(
    cloud_dir,
    "data",
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_gages2_etc_20250517+cluster.csv",
)
cara_attrs = pd.read_csv(cara_attrs_path, index_col=0)
cara_attrs
# %%
print("Loading GAGES2 attributes...")
gages2_attrs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
gages2_attrs = pd.read_csv(gages2_attrs_path)
gages2_attrs["gauge_id"] = "gages2_" + gages2_attrs["STAID"].astype(str).str.zfill(8)
gages2_attrs.set_index("gauge_id", inplace=True)


# %%
print("Concatenating Caravan and GAGES2 signatures and watershed shapefiles...")
sigs = pd.concat(
    [sigs_obs_cara, sigs_obs_gg2, sigs_pred_gg2, sigs_pred_hys_gg2, sigs_pred_hys],
    axis=0,
)
print(f"Number of gauges in sigs: {len(sigs)}")

wspolygon = pd.concat(
    [
        wspolygon_camels,
        wspolygon_hysets,
        gages2_wspolygon.drop(columns=["AREA", "PERIMETER", "GAGE_ID", "usgs_gauge"]),
    ],
    ignore_index=True,
)
wspolygon.set_index("gauge_id", inplace=True)

if "gauge_id" in sigs.columns:
    sigs.set_index("gauge_id", inplace=True)
sigs = sigs.join(wspolygon, how="left")

print("Joining Caravan attributes...")
sigs = sigs.join(cara_attrs, how="left")
print(f"Number of gauges in sigs: {len(sigs)}")
sigs.tail()

print("Joining GAGES2 attributes...")
sigs = sigs.join(gages2_attrs, how="left", lsuffix="", rsuffix="_gages2")
print(f"Number of gauges in sigs: {len(sigs)}")

sigs.tail()
# %%
print("Curating data...")
sigs = gpd.GeoDataFrame(sigs, geometry="geometry", crs=4326)
sigs["area"] = sigs.geometry.values.area
# sigs = sigs.sort_values(by="order", ascending=True)
sigs = sigs.sort_values(by="area", ascending=False)

# %%
# #################################################
# Calculate signature statistics
# ################################################
sigs["diff_RCPint_RCPvol"] = sigs["R_Pint_RC"] - sigs["R_Pvol_RC"]
# Mask where both R_Pint_RC and R_Pvol_RC are negative
sigs["diff_RCPint_RCPvol_masked"] = sigs["diff_RCPint_RCPvol"].mask(
    (sigs["R_Pint_RC"] < 0) & (sigs["R_Pvol_RC"] < 0)
)

# %% #######################################
# Filter out gauges with snow data below a threshold
############################################
frac_snow_thresh = 0.2
sigs_filt = sigs[
    (
        (sigs["SNOW_PCT_PRECIP"] < frac_snow_thresh * 100)
        | (~sigs["SNOW_PCT_PRECIP"].isna())
    )
    | (
        (sigs["SNOW_FRAC_PRECIP"] < frac_snow_thresh)
        | (~sigs["SNOW_FRAC_PRECIP"].isna())
    )
    | ((sigs["SNOWICENLCD06"] < frac_snow_thresh) | (~sigs["SNOWICENLCD06"].isna()))
    | (
        (sigs["SNOW_PCT_PRECIP_gages2"] < frac_snow_thresh * 100)
        | (~sigs["SNOW_PCT_PRECIP_gages2"].isna())
    )
    | (
        (sigs["SNOWICENLCD06_gages2"] < frac_snow_thresh)
        | (~sigs["SNOWICENLCD06_gages2"].isna())
    )
]
print(
    f"Number of gauges in sigs_filt: {len(sigs_filt)} ({len(sigs_filt) / len(sigs) * 100:.1f}%)"
)
sigs_filt

# %% Zenodo CSV (same destination pattern as export_sigs_and_processes.py)
_wu_csv = sigs_filt.drop(columns=["geometry"], errors="ignore").copy()
_wu_csv["gauge_id"] = _wu_csv.index.astype(str)
_wu_csv["gauge_num"] = (
    _wu_csv["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)
_wu_base_cols = [
    "gauge_id",
    "gauge_num",
    "gauge_name",
    "gauge_lat",
    "gauge_lon",
    "data_name",
]
_wu_sig_cols = [
    "R_Pint_RC",
    "R_Pvol_RC",
    "diff_RCPint_RCPvol",
    "diff_RCPint_RCPvol_masked",
]
_wu_out_cols = [c for c in _wu_base_cols + _wu_sig_cols if c in _wu_csv.columns]
_wu_out_path = os.path.join(zenodo_dir, "sigs_Wu_RC_components.csv")
_wu_csv[_wu_out_cols].to_csv(_wu_out_path, index=False)
print(f"Wrote {_wu_out_path} ({len(_wu_csv)} rows, columns: {_wu_out_cols})")

# Polygon GeoJSON (same attributes as CSV + geometry; polygons already simplified before join)
_wu_poly_cols = [c for c in _wu_out_cols if c in sigs_filt.columns and c != "gauge_id"]
_wu_poly = sigs_filt[_wu_poly_cols + ["geometry"]].copy()
_wu_poly.insert(0, "gauge_id", sigs_filt.index.astype(str))
if "gauge_num" in _wu_out_cols and "gauge_num" not in _wu_poly.columns:
    _wu_poly.insert(
        1,
        "gauge_num",
        _wu_poly["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8),
    )
_wu_poly_path = os.path.join(zenodo_dir, "sigs_Wu_RC_components_polygons.geojson")
_wu_poly.to_file(_wu_poly_path, driver="GeoJSON")
print(f"Wrote {_wu_poly_path} ({len(_wu_poly)} features)")
