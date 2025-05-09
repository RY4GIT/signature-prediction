# %%
import os
import glob
import geopandas as gpd
import pandas as pd

# %%
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"

# %%
gages2_shp_dir = os.path.join(
    data_dir,
    "GAGES2",
    "GAGES_II_Geospa",
    "boundaries_shapefiles_by_aggeco",
)
# Find all .shp files in the directory
shapefile_paths = glob.glob(os.path.join(gages2_shp_dir, "*.shp"))
print(f"Found {len(shapefile_paths)} shapefiles in directory")

# Read each shapefile into a GeoDataFrame and store in a dictionary
gages2_polygons = {}
for shapefile_path in shapefile_paths:
    # Extract the filename without extension to use as dictionary key
    filename = os.path.splitext(os.path.basename(shapefile_path))[0]
    print(f"Reading {filename}...")

    # Read the shapefile and project to EPSG:4326
    gdf = gpd.read_file(shapefile_path).to_crs(epsg=4326)
    gages2_polygons[filename] = gdf

    # Print some info about the shapefile
    print(f"  - Contains {len(gdf)} features")

# If you want to combine all shapefiles into one GeoDataFrame
# Be careful with this if the shapefiles have different schemas
if gages2_polygons:
    all_gages2_polygons = pd.concat(gages2_polygons.values(), ignore_index=True)
    print(f"Combined GeoDataFrame contains {len(all_gages2_polygons)} features")
else:
    print("No shapefiles found in directory")

# Save the combined GeoDataFrame to a shapefile
output_shapefile_path = os.path.join(
    data_dir, "GAGES2", "GAGES_II_Geospa", "all_gages2_polygons.shp"
)
