# %%
import geopandas as gpd
import os
import pandas as pd
import math

# %%
gages2_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_Geospa"
gages2_polygons = gpd.read_file(os.path.join(gages2_dir, "all_gages2_polygons.shp"))

# %%
gages2_polygons.columns
# %%
print(f"There are {len(gages2_polygons)} gages2 polygons")
# %% Get the polygon subset that is NOT overlapping with the Caravan gages
cara_attrs = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv"
cara_attrs = pd.read_csv(cara_attrs)
cara_attrs["usgs_gauge_id"] = (
    cara_attrs["gauge_id"].astype(str).str.split("_").str[1].astype(str).str.zfill(8)
)
print(f"There are {len(cara_attrs)} Caravan gages")

cara_subset = cara_attrs[~cara_attrs["DRAIN_SQKM"].isna()]
print(f"There are {len(cara_subset)} Caravan gages with no area")
# %%
gages2_polygons["usgs_gauge_id"] = gages2_polygons["GAGE_ID"].astype(str).str.zfill(8)

# %%
gages2_polygons_not_cara = gages2_polygons[
    ~gages2_polygons["usgs_gauge_id"].isin(cara_subset["usgs_gauge_id"])
]
print(
    f"There are {len(gages2_polygons_not_cara)} gages2 polygons that are not Caravan gages"
)

# Make sure its within the CONUS
conus_bbox = (24.5, -124.7, 49.4, -66.9)
length_before = len(gages2_polygons_not_cara)
gages2_polygons_not_cara = gages2_polygons_not_cara[
    gages2_polygons_not_cara.geometry.bounds.miny > conus_bbox[0]
]
gages2_polygons_not_cara = gages2_polygons_not_cara[
    gages2_polygons_not_cara.geometry.bounds.minx > conus_bbox[1]
]
gages2_polygons_not_cara = gages2_polygons_not_cara[
    gages2_polygons_not_cara.geometry.bounds.maxy < conus_bbox[2]
]
gages2_polygons_not_cara = gages2_polygons_not_cara[
    gages2_polygons_not_cara.geometry.bounds.maxx < conus_bbox[3]
]
print(
    f"There are {len(gages2_polygons_not_cara)} Caravan+GAGES2 gauges after dropping {length_before - len(gages2_polygons_not_cara)} gauges not in CONUS based on lat/lon"
)
# %%
gages2_polygons_not_cara.to_file(
    os.path.join(gages2_dir, "gages2_polygons_not_cara.shp"), driver="ESRI Shapefile"
)

# # %% Divide basins into 6 files
# import math

# batch_size = 600
# n_batches = math.ceil(len(gages2_polygons_not_cara) / batch_size)
# for i in range(n_batches):
#     print(f"Dividing into {n_batches} files, processing file {i + 1} of {n_batches}")
#     if i == n_batches - 1:
#         gages2_polygons_not_cara.iloc[i * batch_size :].to_file(
#             os.path.join(gages2_dir, f"gages2_polygons_not_cara_{i + 1}.shp"),
#             driver="ESRI Shapefile",
#         )
#     else:
#         gages2_polygons_not_cara.iloc[i * batch_size : (i + 1) * batch_size].to_file(
#             os.path.join(gages2_dir, f"gages2_polygons_not_cara_{i + 1}.shp"),
#             driver="ESRI Shapefile",
#         )

# # %%
