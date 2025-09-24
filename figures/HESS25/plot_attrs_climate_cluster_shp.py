# %% Script to save the climate cluster points as a shapefile
import os
import pandas as pd
import geopandas as gpd

# %% Save it as point data in a shapefile
# Have to read from here because the gauge_id has been dropped in the data_scaled_df
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
attr_file = os.path.join(
    cloud_dir,
    "data",
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_gages2_etc_20250517+cluster.csv",
)
attrs = pd.read_csv(attr_file)
attrs["gauge_num"] = attrs["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
attrs.dropna(subset=["cluster"], inplace=True)
# %%
# HYSETS poluygons
local_dir = r"D:\data"
hysets_polygon_file = os.path.join(
    local_dir,
    "Caravan1.4",
    "shapefiles",
    "hysets",
    "hysets_basin_shapes.shp",
)
hysets_polygon = gpd.read_file(hysets_polygon_file).to_crs(epsg=4326)
# %%
hysets_polygon["gauge_num"] = (
    hysets_polygon["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)

# %%
# Merge with hysets polygons
df = attrs.merge(
    hysets_polygon,
    left_on="gauge_num",
    right_on="gauge_num",
    how="left",
    suffixes=("", "_polygons"),
)
gdf = gpd.GeoDataFrame(
    df[["gauge_id", "cluster", "geometry", "gauge_num", "gauge_lat", "gauge_lon"]],
    geometry="geometry",
    crs="EPSG:4326",
)
print(len(gdf))
gdf.head()

# %%
shp_dir = os.path.join(cloud_dir, "figs", "fig_geographic_region")
gdf.to_file(
    os.path.join(shp_dir, "climate_clusters_points.shp"), driver="ESRI Shapefile"
)
