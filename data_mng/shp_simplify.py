# %% Simplify the shapefile

import geopandas as gpd
import os
import pandas as pd

website_dir = r"C:\Users\flipl\dev\ry4git.github.io\docs\shp"
# %% ##############################################################
# CAMELS US
###################################################################

cara_path = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4"
)


def process_caravan(cara_path, data_name, out_dir):
    file_path = os.path.join(
        cara_path, "shapefiles", data_name, f"{data_name}_basin_shapes.shp"
    )
    attrs_path = os.path.join(
        cara_path, "attributes", data_name, f"attributes_other_{data_name}.csv"
    )

    # Read the shapefile
    gdf = gpd.read_file(file_path)
    attrs = pd.read_csv(attrs_path)

    # Merge the attributes with the shapefile
    gdf = gdf.merge(attrs, on="gauge_id", how="left")
    gdf.head()

    # Simplify the shapefile
    gdf_simplified = gdf.copy()
    gdf_simplified.geometry = gdf.simplify(tolerance=0.02)
    gdf_simplified["Catchment area (km2)"] = gdf["area"]
    gdf_simplified.sort_values(by="Catchment area (km2)", ascending=False, inplace=True)
    gdf_simplified["Gauge ID"] = gdf["gauge_id"].astype(str).str.split("_").str[1]
    gdf_simplified["Gauge name"] = gdf["gauge_name"]

    print(gdf_simplified.head())

    # Save the simplified shapefile
    gdf_simplified[
        [
            "Gauge ID",
            "Gauge name",
            "Catchment area (km2)",
            "geometry",
        ]
    ].to_file(
        os.path.join(out_dir, "shapes_simplified.geojson"),
        driver="GeoJSON",
        features=True,
        properties=[
            "Gauge ID",
            "Gauge name",
            "Catchment area (km2)",
        ],
    )

    # Make a point geometry from the gauge_lat and gauge_lon
    gdf_gauge = gpd.GeoDataFrame(
        gdf_simplified[
            ["Gauge ID", "Gauge name", "Catchment area (km2)", "gauge_lat", "gauge_lon"]
        ],
        geometry=gpd.points_from_xy(
            gdf_simplified["gauge_lon"], gdf_simplified["gauge_lat"]
        ),
    )

    # Save the point geometry
    gdf_gauge.to_file(
        os.path.join(out_dir, "gauge_points.geojson"),
        driver="GeoJSON",
        features=True,
    )


# %%
# process_caravan(cara_path, "camels", os.path.join(website_dir, "camels_us"))
# process_caravan(cara_path, "hysets", os.path.join(website_dir, "hysets_us"))


# %% ##########################################################
#  GAGES2
###################################################################

file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_Geospa\all_gages2_polygons.shp"
gdf = gpd.read_file(file_path)
gdf.head()


# %%
attrs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
attrs = pd.read_csv(
    attrs_path,
)
selected_cols = [
    "STANAME",
    "DRAIN_SQKM",
    "LAT_GAGE",
    "LNG_GAGE",
    "CLASS",
    "STAID",
]
attrs_subset = attrs[selected_cols].copy()

# Make the usgs_gauge_id a string
attrs_subset["STAID"] = attrs_subset["STAID"].astype(str).str.zfill(8)
# Make the GAGE_ID a string
gdf["GAGE_ID"] = gdf["GAGE_ID"].astype(str).str.zfill(8)

# Merge the attributes with the shapefile
gdf = gdf.merge(attrs_subset, left_on="GAGE_ID", right_on="STAID", how="left")
# %%
gdf_simplified = gdf.copy()
gdf_simplified.geometry = gdf.simplify(tolerance=0.02)
gdf_simplified["Catchment area (km2)"] = gdf["DRAIN_SQKM"]
gdf_simplified.sort_values(by="Catchment area (km2)", ascending=False, inplace=True)
gdf_simplified["Gauge ID"] = gdf["GAGE_ID"]
gdf_simplified["Gauge name"] = gdf["STANAME"]
gdf_simplified["Reference class"] = gdf["CLASS"]


# %%
gdf_simplified.head()
# %%
# Save the simplified shapefile
gdf_simplified[
    [
        "Gauge ID",
        "Gauge name",
        "Catchment area (km2)",
        "geometry",
        "Reference class",
    ]
].to_file(
    os.path.join(website_dir, "gages2_us", "shapes_simplified.geojson"),
    driver="GeoJSON",
    features=True,
    properties=[
        "Gauge ID",
        "Gauge name",
        "Catchment area (km2)",
        "Reference class",
    ],
)

# Make a point geometry from the gauge_lat and gauge_lon
gdf_gauge = gpd.GeoDataFrame(
    gdf_simplified[
        ["Gauge ID", "Gauge name", "Catchment area (km2)", "LAT_GAGE", "LNG_GAGE"]
    ],
    geometry=gpd.points_from_xy(gdf_simplified["LNG_GAGE"], gdf_simplified["LAT_GAGE"]),
)

# Save the point geometry
gdf_gauge.to_file(
    os.path.join(website_dir, "gages2_us", "gauge_points.geojson"),
    driver="GeoJSON",
    features=True,
)

# %%
