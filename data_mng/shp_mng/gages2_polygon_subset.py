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
# %% Further subset it to exclude gages with streamflow records
gages2_sig_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\gages2_20250608\out_calc_All_custom_filt_qc_snow.csv"
gages2_sig = pd.read_csv(gages2_sig_file)
gages2_sig["usgs_gauge_id"] = gages2_sig["gauge_id"].astype(str).str.zfill(8)
gages2_sig = gages2_sig[~gages2_sig["BFI"].isna()]
print(f"There are {len(gages2_sig)} gages with streamflow records")

# %%
gages2_polygons_not_cara["usgs_gauge_id"] = gages2_polygons_not_cara[
    "usgs_gauge_id"
].astype(str)
gages2_sig["usgs_gauge_id"] = gages2_sig["usgs_gauge_id"].astype(str)
gages2_polygons_need_pred = gages2_polygons_not_cara[
    ~gages2_polygons_not_cara["usgs_gauge_id"].isin(gages2_sig["usgs_gauge_id"])
]
print(f"There are {len(gages2_polygons_need_pred)} gages without streamflow records")

# %%
gages2_polygons_need_pred.geometry
# %%


def check_closed_polygons(gdf):
    """
    Check if polygons in a GeoDataFrame are closed.
    Returns a DataFrame with information about closed/open polygons.
    """
    # Create a list to store results
    results = []

    # Check each polygon
    for idx, row in gdf.iterrows():
        geom = row.geometry
        is_closed = True

        # Get coordinates
        coords = list(geom.exterior.coords)

        # Check if first and last points are the same
        if coords[0] != coords[-1]:
            is_closed = False

        results.append(
            {
                "gauge_id": row["GAGE_ID"],
                "is_closed": is_closed,
                "area": geom.area,
                "num_points": len(coords),
            }
        )

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Print summary
    total = len(results_df)
    closed = results_df["is_closed"].sum()
    print(f"Total polygons: {total}")
    print(f"Closed polygons: {closed}")
    print(f"Open polygons: {total - closed}")

    return results_df


def fix_open_polygons(gdf):
    """
    Fix open polygons in a GeoDataFrame by ensuring they are closed.
    Returns a new GeoDataFrame with fixed polygons.
    """
    from shapely.geometry import Polygon, LineString
    from shapely.ops import polygonize

    # Create a copy of the GeoDataFrame
    gdf_fixed = gdf.copy()

    # Track changes
    fixed_count = 0

    # Process each polygon
    for idx, row in gdf_fixed.iterrows():
        geom = row.geometry

        # Get the coordinates
        coords = list(geom.exterior.coords)

        # If the first and last points are not the same, add the first point at the end
        if coords[0] != coords[-1]:
            coords.append(coords[0])

            # Create a new closed polygon
            new_polygon = Polygon(coords)

            # Update the geometry
            gdf_fixed.at[idx, "geometry"] = new_polygon
            fixed_count += 1

    print(f"Fixed {fixed_count} open polygons")

    # Verify all polygons are now closed
    closed_check = check_closed_polygons(gdf_fixed)

    return gdf_fixed


def ensure_valid_polygons(gdf):
    """
    Ensure all polygons are valid and closed.
    Returns a new GeoDataFrame with valid polygons.
    """
    from shapely.geometry import Polygon
    from shapely.validation import make_valid

    # Create a copy of the GeoDataFrame
    gdf_valid = gdf.copy()

    # Track changes
    fixed_count = 0

    # Process each polygon
    for idx, row in gdf_valid.iterrows():
        geom = row.geometry

        # Make the geometry valid
        valid_geom = make_valid(geom)

        # If it's a polygon, ensure it's closed
        if isinstance(valid_geom, Polygon):
            coords = list(valid_geom.exterior.coords)
            if coords[0] != coords[-1]:
                coords.append(coords[0])
                valid_geom = Polygon(coords)

        # Update the geometry
        gdf_valid.at[idx, "geometry"] = valid_geom
        fixed_count += 1

    print(f"Fixed {fixed_count} polygons")

    # Verify all polygons are now closed
    closed_check = check_closed_polygons(gdf_valid)

    return gdf_valid


# Check if polygons are closed
print("Initial check:")
closed_check = check_closed_polygons(gages2_polygons_need_pred)

# Fix open polygons
print("\nFixing polygons:")
gages2_polygons_need_pred = fix_open_polygons(gages2_polygons_need_pred)

# Ensure all polygons are valid
print("\nEnsuring valid polygons:")
gages2_polygons_need_pred = ensure_valid_polygons(gages2_polygons_need_pred)

# %%
gages2_polygons_need_pred.to_file(
    os.path.join(gages2_dir, "gages2_polygons_need_pred.shp"), driver="ESRI Shapefile"
)

# %%
print(
    f"Saved {len(gages2_polygons_need_pred)} gages with valid polygons to {os.path.join(gages2_dir, 'gages2_polygons_need_pred.shp')}"
)

# %%
# Plot the polygons in the map
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Create figure and axes with a specific projection
fig, ax = plt.subplots(figsize=(15, 10), subplot_kw={"projection": ccrs.PlateCarree()})

# Add map features
ax.add_feature(cfeature.STATES.with_scale("50m"), linewidth=0.5)
ax.add_feature(cfeature.COASTLINE.with_scale("50m"))

# Set extent to CONUS
ax.set_extent([-124.7, -66.9, 24.5, 49.4], crs=ccrs.PlateCarree())

# Plot the polygons
gages2_polygons_need_pred.plot(ax=ax, color="red", alpha=0.5, markersize=1, legend=True)

# Add gridlines
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Add title
plt.title("GAGES-II Polygons Needing Prediction")

plt.show()


# %%
