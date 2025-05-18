import geopandas as gpd
import pandas as pd
import os

# Base directory for derived attributes
derived_attrs_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs"
)

# List of shapefile paths relative to the base directory
relative_paths = [
    # r"NWI\conWetland_area_frac_camels.shp",
    # r"NWI\conWetland_area_frac_camels_ecoregions.shp",
    # r"NWI\conWetland_area_frac_hysets4621.shp",
    # r"GIWs\isoWetland_area_frac_camels.shp",
    # r"GIWs\isoWetland_area_frac_hysets4621.shp",
    r"SGMC_Geology\age_weighted_camels.shp",
    r"SGMC_Geology\age_weighted_hysets4621.shp",
    r"SGMC_Geology\age_majorlith_camels.shp",
    r"SGMC_Geology\age_majorlith_hysets4621.shp",
]

# Loop through each shapefile, read it, drop the geometry column, and save to CSV
for relative_path in relative_paths:
    shapefile_path = os.path.join(derived_attrs_dir, relative_path)

    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)

    # Drop the geometry column
    df = gdf.drop(columns="geometry")

    # Create a CSV output path based on the shapefile name
    csv_output_path = shapefile_path.replace(".shp", ".csv")

    # Save the DataFrame to a CSV file
    df.to_csv(csv_output_path, index=False)

    print(
        f"Data from {shapefile_path} (except geometry) has been saved to {csv_output_path}"
    )
