# %% Plot signatures from multiple sources (Caravan, GAGES-II, RF predictions)
import glob
import os
import re

import geopandas as gpd


# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")

# Google Drive directory
gdrive_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"

# Local directory (For Caravan data)
local_dir = r"D:\data"


leaflet_json_dir = r"C:\Users\flipl\dev\ry4git.github.io\docs\assets\shp\sig_us"
if not os.path.exists(leaflet_json_dir):
    os.makedirs(leaflet_json_dir)

# Skip these GeoJSONs (many columns / large files). Keep ``sigs_OverlandFlow``; skip Wu ``sigs_OverlandFlowType``.
SIGS_GEOJSON_SKIP_STEMS = frozenset(
    {"sigs_SeasonalVariability", "sigs_OverlandFlowType"}
)


# %% Load sigs_*.geojson (one GeoDataFrame per file; keys = basename without .geojson)
sigs_geojson_dir = r"C:\Users\flipl\dev\ry4git.github.io\docs\assets\shp\sig_us"
sigs_geojson_files = sorted(glob.glob(os.path.join(sigs_geojson_dir, "sigs_*.geojson")))
sigs_gdfs = {}
for _path in sigs_geojson_files:
    _stem = os.path.splitext(os.path.basename(_path))[0]
    if _stem in SIGS_GEOJSON_SKIP_STEMS:
        continue
    _gdf = gpd.read_file(_path)
    if _gdf.crs is not None:
        _gdf = _gdf.to_crs(epsg=4326)
    sigs_gdfs[_stem] = _gdf
print(f"Loaded {len(sigs_gdfs)} GeoJSON layer(s): {list(sigs_gdfs.keys())}")
print(f"Skipped loading (by stem): {sorted(SIGS_GEOJSON_SKIP_STEMS)}")


# %%
def _stem_to_dominance_column(stem):
    """sigs_Baseflow -> baseflow_dominance; sigs_OverlandFlow -> overland_flow_dominance."""
    if not stem.startswith("sigs_"):
        raise ValueError(f"Expected stem 'sigs_*', got {stem!r}")
    proc = stem[len("sigs_") :]
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", proc).lower()
    return f"{snake}_dominance"


def _dominance_to_bool(series):
    if series.dtype == bool:
        return series
    return series.map(
        lambda x: (
            bool(x)
            if isinstance(x, (bool, int, float))
            else str(x).lower() in ("true", "1", "t", "yes")
        )
    )


def _join_keys(gdf):
    if "gauge_id" in gdf.columns and gdf["gauge_id"].notna().any():
        return ["gauge_id"]
    return ["gauge_num", "source", "gauge_name"]


def build_cross_signature_gdf(sigs_gdfs, anchor_stem="sigs_Baseflow"):
    """
    Inner-join process GeoJSONs on gauge_id (preferred) or on gauge_num + source + gauge_name.
    Keeps gauge_id, gauge_name, source, geometry from the anchor layer; adds one bool column
    per layer from ``dominance`` (e.g. baseflow_dominance from sigs_Baseflow).
    Adds ``unclassified`` when both ``baseflow_dominance`` and ``overland_flow_dominance`` exist
    (``sigs_OverlandFlow`` is loaded; ``sigs_OverlandFlowType`` is skipped via ``SIGS_GEOJSON_SKIP_STEMS``).
    """
    stems = sorted(
        s
        for s in sigs_gdfs
        if s.startswith("sigs_") and s not in SIGS_GEOJSON_SKIP_STEMS
    )
    if not stems:
        raise ValueError("No sigs_* layers in sigs_gdfs")
    if anchor_stem not in sigs_gdfs:
        anchor_stem = stems[0]

    base = sigs_gdfs[anchor_stem]
    keys = _join_keys(base)
    for c in keys + ["dominance", "gauge_name", "source", "geometry"]:
        if c not in base.columns:
            raise KeyError(f"Anchor {anchor_stem!r} missing column {c!r}")

    dom_col = _stem_to_dominance_column(anchor_stem)
    out = base[keys + ["gauge_name", "source", "geometry", "dominance"]].copy()
    out[dom_col] = _dominance_to_bool(out["dominance"])
    out = out.drop(columns=["dominance"])

    for stem in stems:
        if stem == anchor_stem:
            continue
        gdf = sigs_gdfs[stem]
        if "dominance" not in gdf.columns:
            continue
        k = _join_keys(gdf)
        if k != keys:
            raise ValueError(
                f"Join key mismatch: anchor {anchor_stem!r} uses {keys}, {stem!r} uses {k}. "
                "Re-export GeoJSONs with gauge_id, or use consistent columns."
            )
        dc = _stem_to_dominance_column(stem)
        right = gdf[keys + ["dominance"]].copy()
        right[dc] = _dominance_to_bool(right["dominance"])
        right = right.drop(columns=["dominance"])
        out = out.merge(right, on="gauge_id", how="outer")

    dom_cols = [c for c in out.columns if c.endswith("_dominance")]
    bf, oflow = "baseflow_dominance", "overland_flow_dominance"
    extra_cols = []
    if bf in out.columns and oflow in out.columns:
        out["unclassified"] = out[bf].eq(False) & out[oflow].eq(False)
        extra_cols = ["unclassified"]

        out["both_dominant"] = out[bf].eq(True) & out[oflow].eq(True)
        extra_cols += ["both_dominant"]

    base_cols = [c for c in ("gauge_id", "gauge_name", "source") if c in out.columns]
    if "gauge_id" not in out.columns and "gauge_num" in out.columns:
        base_cols = ["gauge_num", "gauge_name", "source"]
    out = out[base_cols + ["geometry"] + dom_cols + extra_cols]
    return gpd.GeoDataFrame(out, geometry="geometry", crs=base.crs)


def sort_polygons_area_descending(gdf, equal_area_epsg=5070):
    """
    Sort by polygon area in an equal-area CRS (largest first, smallest last) so small
    watersheds draw on top in Leaflet. Returns GeoDataFrame in the original CRS.
    """
    out = gdf.copy()
    orig = out.crs if out.crs is not None else "EPSG:4326"
    out = out.to_crs(equal_area_epsg)
    out["_area_m2"] = out.geometry.area
    out = out.sort_values("_area_m2", ascending=False).drop(columns=["_area_m2"])
    out = out.to_crs(orig)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=orig)


# %%
print("Building cross-signature GeoDataFrame...")
cross_sig_gdf = build_cross_signature_gdf(sigs_gdfs)
print("Sorting polygons by area descending...")
cross_sig_gdf = sort_polygons_area_descending(cross_sig_gdf)
cross_sig_gdf.head()


# %%
cross_sig_geojson = os.path.join(
    leaflet_json_dir, "sigs_cross_process_dominance.geojson"
)
cross_sig_gdf = cross_sig_gdf.reset_index(drop=True)
cross_sig_gdf.to_file(cross_sig_geojson, driver="GeoJSON")
print(f"Wrote {len(cross_sig_gdf)} features to {cross_sig_geojson}")

# %%
