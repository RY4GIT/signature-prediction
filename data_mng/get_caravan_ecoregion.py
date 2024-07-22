# %%
import os
import geopandas as gpd

# %%
# 1. Use ArcGIS Pro to get intersection between the following data (the path are examples)

# Caravan data polygons
# sheds_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles"
# subset_name = "camels"
# sheds_filename = f"{subset_name}_basin_shapes.shp"
# sheds = gpd.read_file(os.path.join(sheds_dir, subset_name, sheds_filename))

# Ecoregion data polygon
# geodata_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data"
# geodata_name = "EcoRegions"
# geodata_filename = "NA_CEC_Eco_Level1.shp"
# geodata = gpd.read_file(os.path.join(geodata_dir, geodata_name, geodata_filename))

# Use "Intersect (Analysis)" tool to get the intersection of two polygon layers
# https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/intersect.htm

# It returns all the intersected polygons for each watershed
# The following script get the max intersecting area for each watershed

# %%
# Config
subset_name = "hysets"  # "camels" or "hysets"
gis_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\gis"
output_path = os.path.join(gis_dir, r"gauge_classify\Ecoregion_max_intrsct")
attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\EcoRegions"
# %%
# Load data
intrsct = gpd.read_file(
    os.path.join(gis_dir, r"gauge_classify\gauge_classify.gdb"),
    driver="FileGDB",
    layer=f"{subset_name}_Intersect_Ecoregion",
)
intrsct.head()

# %%
if subset_name == "camels":
    intrsct.drop(
        columns={"Shape_Length", "Shape_Leng", f"FID_{subset_name}_basin_shapes"},
        inplace=True,
    )
elif subset_name == "hysets":
    intrsct.drop(
        columns={
            "Shape_Length",
            "Shape_Leng",
            f"FID_{subset_name}_basin_shapes_resaved_via_qgis",
        },
        inplace=True,
    )

# Get the row with the maximum intersecting area for each watershed
max_intrsct = intrsct.loc[intrsct.groupby("gauge_id")["Shape_Area"].idxmax()]

# Output
max_intrsct.to_file(os.path.join(output_path, f"Ecoregion_{subset_name}.shp"))

# %%
# Ouptut in CSV format
_shp = gpd.read_file(os.path.join(output_path, f"Ecoregion_{subset_name}.shp"))
shp = _shp[["gauge_id", "NA_L1KEY"]].rename(columns={"NA_L1KEY": "ecoregion"}).copy()
print(shp["ecoregion"].unique())
print(shp.groupby("ecoregion").count())
shp.to_csv(os.path.join(attrs_dir, f"Ecoregion_{subset_name}.csv"), index=False)

# %%

# %% The following code didn't work for some reason (Probably CRS issue for NA_CEC_Eco_Level1.shp)
# # %%
# sheds_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\shapefiles"
# subset_name = "camels"
# sheds_filename = f"{subset_name}_basin_shapes.shp"
# geodata_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data"
# geodata_name = "EcoRegions"
# geodata_filename = "NA_CEC_Eco_Level1.shp"

# # %%
# # Load your data
# sheds = gpd.read_file(os.path.join(sheds_dir, subset_name, sheds_filename))
# geodata = gpd.read_file(os.path.join(geodata_dir, geodata_name, geodata_filename))
# # %%
# # Assuming the target polygon is a single polygon in the GeoDataFrame
# shed = sheds.iloc[0]
# shed_gdf = gpd.GeoDataFrame([shed], geometry="geometry", crs=sheds.crs)
# # Find the intersection
# attr_in_shed = gpd.overlay(geodata, shed_gdf, how="intersection").explode(
#     index_parts=True
# )
# attr_in_shed["area"] = attr_in_shed["geometry"].area
# attr_in_shed.drop(columns={"Shape_Leng", "Shape_Area"})
# out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\attrs"
# out_filename = "test.shp"
# attr_in_shed.to_file(os.path.join(out_dir, out_filename))
# # %%

# # %%
# # Calculate the area of the intersections
# intersections["area"] = intersections["intersection"].area

# # Find the polygon with the largest intersected area
# largest_intersection = intersections.loc[intersections["area"].idxmax()]

# # Output the largest intersection
# largest_intersection_gdf = gpd.GeoDataFrame(
#     [largest_intersection], crs=other_polygons.crs
# )
# print(target_polygon)
# print(intersections)
# print(largest_intersection_gdf)

# # %%
