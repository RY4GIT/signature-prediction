# %%
import geopandas as gpd
import os

# %%
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_Geospa"
shp_file = "gages2_polygons_not_cara.shp"
shp_path = os.path.join(data_dir, shp_file)

# %%
shp_gdf = gpd.read_file(shp_path)

# %%
csv_filename = shp_file.replace(".shp", ".csv")
shp_gdf.drop(columns=["geometry"]).to_csv(
    os.path.join(data_dir, csv_filename), index=False
)

# %%
