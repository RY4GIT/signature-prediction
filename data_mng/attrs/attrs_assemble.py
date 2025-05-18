# %%
import pandas as pd
import numpy as np
import os

# %% ##############################################################
# ASSEMBLE ATTRIBUTES
##################################################################


def load_and_concat_datasets(hysets_file, camels_file, dataset_name=""):
    """Load and concatenate HYSETS and CAMELS datasets."""
    hysets_data = pd.read_csv(hysets_file)
    camels_data = pd.read_csv(camels_file)

    # Ensure gauge_id is treated as string
    hysets_data["gauge_id"] = hysets_data["gauge_id"].astype(str)
    camels_data["gauge_id"] = camels_data["gauge_id"].astype(str)

    # Add prefixes if needed
    if not any(camels_data["gauge_id"].str.startswith("camels_")):
        camels_data["gauge_id"] = "camels_" + camels_data["gauge_id"].str.zfill(8)

    # Concatenate vertically (axis=0) to stack the rows
    combined_data = pd.concat([hysets_data, camels_data], axis=0)

    # Create usgs_gauge_id before setting index
    combined_data["usgs_gauge_id"] = (
        combined_data["gauge_id"].str.replace("camels_", "").str.replace("hysets_", "")
    )

    # Set gauge_id as index after concatenation
    combined_data.set_index("gauge_id", inplace=True)

    if dataset_name:
        print(f"\n{dataset_name}")
    print(f"{len(hysets_data)} hysets gauges")
    print(f"{len(camels_data)} camels gauges")

    return combined_data


# Base directories
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
assembled_attrs_dir = os.path.join(data_dir, "derived_attrs", "assembled_RA")
caravan_attrs_dir = os.path.join(data_dir, "Caravan1.5", "attributes")
ecoregion_dir = os.path.join(data_dir, "derived_attrs", "Ecoregions")


# ##############################################################################
# Load Caravan attributes
cara_attrs = load_and_concat_datasets(
    os.path.join(caravan_attrs_dir, "hysets", "attributes_caravan_hysets.csv"),
    os.path.join(caravan_attrs_dir, "camels", "attributes_caravan_camels.csv"),
    "Caravan Attributes",
)
print(f"{len(cara_attrs)} total gauges")

cara_HA_attrs = load_and_concat_datasets(
    os.path.join(caravan_attrs_dir, "hysets", "attributes_hydroatlas_hysets.csv"),
    os.path.join(caravan_attrs_dir, "camels", "attributes_hydroatlas_camels.csv"),
    "Caravan HydroAtlas Attributes",
)
print(f"{len(cara_HA_attrs)} total gauges")

cara_geo_attrs = load_and_concat_datasets(
    os.path.join(caravan_attrs_dir, "hysets", "attributes_other_hysets.csv"),
    os.path.join(caravan_attrs_dir, "camels", "attributes_other_camels.csv"),
    "Caravan Geographic Attributes",
)
print(f"{len(cara_geo_attrs)} total gauges")

# Load GIW attributes
giw_dir = os.path.join(data_dir, "derived_attrs", "GIWs")
cara_giw = load_and_concat_datasets(
    os.path.join(giw_dir, "isoWetland_area_frac_hysets12162.csv"),
    os.path.join(giw_dir, "isoWetland_area_frac_camels.csv"),
    "GIWs",
)

# Load NWI attributes
nwi_dir = os.path.join(data_dir, "derived_attrs", "NWI")
cara_niw = load_and_concat_datasets(
    os.path.join(nwi_dir, "conWetland_area_frac_hysets12162.csv"),
    os.path.join(nwi_dir, "conWetland_area_frac_camels.csv"),
    "NWI",
)

# Load SGMC Geology attributes
sgmc_dir = os.path.join(data_dir, "derived_attrs", "SGMC_Geology")
cara_agemajor = load_and_concat_datasets(
    os.path.join(sgmc_dir, "age_majorlith_hysets12162.csv"),
    os.path.join(sgmc_dir, "age_majorlith_camels.csv"),
    "SGMC Major Lithology",
)

cara_ageweighted = load_and_concat_datasets(
    os.path.join(sgmc_dir, "age_weighted_hysets12162.csv"),
    os.path.join(sgmc_dir, "age_weighted_camels.csv"),
    "SGMC Weighted Age",
)

cara_ecoregion = load_and_concat_datasets(
    os.path.join(ecoregion_dir, "Ecoregion_hysets.csv"),
    os.path.join(ecoregion_dir, "Ecoregion_camels.csv"),
    "EPA Ecoregions ",
)

# %%
cara_niw.drop(columns=["0", "est"], inplace=True)
# %% ##############################################################################
# Load a few other attributes
hammond_clim_dir = os.path.join(data_dir, "GAGES2", "climate_attrs_Hammond")
hammond_clim_attrs = pd.read_csv(
    os.path.join(hammond_clim_dir, "mean_annual_climate_attributes.csv")
)
hammond_clim_attrs["usgs_gauge_id"] = (
    hammond_clim_attrs["gageID"].astype(str).str.zfill(8)
)
hammond_clim_attrs.drop(columns=["Unnamed: 0"], inplace=True)
hammond_clim_attrs.head()
print("Hammond climate attributes for GAGES2 gauges")
print(len(hammond_clim_attrs))

# %%
morph_file = os.path.join(
    data_dir, "Prancevic_et_al_2025", "science.ado2860_data_s2.csv"
)
_morph_attrs = pd.read_csv(morph_file)
_morph_attrs["usgs_gauge_id"] = (
    _morph_attrs["gauge_id"].astype(int).astype(str).str.zfill(8)
)
morph_attrs = _morph_attrs[
    [
        "p99_pave",
        "dammed_portion",
        "dam_complete",
        "slope_pct",
        "drainage_area",
        "beta_ave",
        "cv_q",
        "cv_l",
        "fact_l_98",
        "usgs_gauge_id",
    ]
].copy()
morph_attrs.head()
print("Morph attributes")
print(len(morph_attrs))

# %%
gages2_attrs_file = os.path.join(
    data_dir, "GAGES2", "GAGES_II_attrs", "gagesII_sept30_2011_concat.csv"
)
gages2_attrs = pd.read_csv(gages2_attrs_file)
gages2_attrs["usgs_gauge_id"] = gages2_attrs["usgs_gauge_id"].astype(str).str.zfill(8)
print("GAGES2 attributes")
print(len(gages2_attrs))

# %%
# ##############################################################################
# Assemble attributes
# Use cara_attrs as the template and left join all other attributes
# ##############################################################################
# First, join attributes with gauge_id as index
assembled_attrs = cara_attrs.copy()
original_cara_attrs_columns = assembled_attrs.columns.tolist()

for attr_df, attr_name in [
    (cara_HA_attrs, "HydroAtlas"),
    (cara_geo_attrs, "Geographic"),
    (cara_giw, "GIW"),
    (cara_niw, "NWI"),
    (cara_agemajor, "Age Major"),
    (cara_ageweighted, "Age Weighted"),
    (cara_ecoregion, "Ecoregion"),
]:
    print(f"Adding {attr_name} attributes...")

    # Find overlapping columns
    overlap_cols = list(set(attr_df.columns) & set(assembled_attrs.columns))

    # If overlapping columns exist, temporarily rename them in attr_df
    temp_rename_dict = {col: f"{col}_temp" for col in overlap_cols}
    if temp_rename_dict:
        attr_df_copy = attr_df.copy()
        attr_df_copy.rename(columns=temp_rename_dict, inplace=True)
        assembled_attrs = assembled_attrs.join(attr_df_copy, how="left")

        # For each overlapping column, use cara_attrs values where available
        for orig_col, temp_col in temp_rename_dict.items():
            assembled_attrs[orig_col] = assembled_attrs[orig_col].combine_first(
                assembled_attrs[temp_col]
            )
            assembled_attrs.drop(columns=[temp_col], inplace=True)
    else:
        # No overlapping columns, do a regular join
        assembled_attrs = assembled_attrs.join(attr_df, how="left")

# For datasets with usgs_gauge_id (not indexed), merge on usgs_gauge_id
for attr_df, attr_name in [
    (hammond_clim_attrs, "Hammond Climate"),
    (morph_attrs, "Morphological"),
    (gages2_attrs, "GAGES2"),
]:
    print(f"Adding {attr_name} attributes...")

    # Set usgs_gauge_id as index for the joining dataset temporarily
    attr_df_copy = attr_df.copy().set_index("usgs_gauge_id")

    # Find overlapping columns
    overlap_cols = list(set(attr_df_copy.columns) & set(assembled_attrs.columns))

    # If overlapping columns exist, temporarily rename them in attr_df
    temp_rename_dict = {col: f"{col}_temp" for col in overlap_cols}
    if temp_rename_dict:
        attr_df_copy.rename(columns=temp_rename_dict, inplace=True)
        assembled_attrs = assembled_attrs.join(
            attr_df_copy, on="usgs_gauge_id", how="left"
        )

        # For each overlapping column, use cara_attrs values where available
        for orig_col, temp_col in temp_rename_dict.items():
            assembled_attrs[orig_col] = assembled_attrs[orig_col].combine_first(
                assembled_attrs[temp_col]
            )
            assembled_attrs.drop(columns=[temp_col], inplace=True)
    else:
        # No overlapping columns, do a regular join
        assembled_attrs = assembled_attrs.join(
            attr_df_copy, on="usgs_gauge_id", how="left"
        )

# Report final assembled attributes
print("\nFinal assembled attributes:")
print(f"Number of gauges: {len(assembled_attrs)}")
print(f"Number of attributes: {assembled_attrs.shape[1]}")

print(f"Length of the Caravan attributes: {len(cara_attrs)}")
# Save the assembled attributes
output_file = os.path.join(assembled_attrs_dir, "attrs_cara_gages2_etc_20250517.csv")
assembled_attrs.to_csv(output_file)
print(f"Saved assembled attributes to {output_file}")


# %%
# ##############################################################################
# Assemble attributes v2
# Use gages2_attrs as the template and left join all other attributes
# ##############################################################################

# Start with gages2_attrs as template
gages2_assembled = gages2_attrs.copy()
# Check for duplicate usgs_gauge_id before setting as index
if gages2_assembled["usgs_gauge_id"].duplicated().any():
    print(
        f"Warning: {gages2_assembled['usgs_gauge_id'].duplicated().sum()} duplicate usgs_gauge_id in gages2_attrs"
    )
    # Keep first occurrence of each usgs_gauge_id
    gages2_assembled = gages2_assembled.drop_duplicates(subset=["usgs_gauge_id"])

gages2_assembled.set_index("usgs_gauge_id", inplace=True)
original_gages2_columns = gages2_assembled.columns.tolist()

print("\nGAGES2-based assembly:")
print(f"Starting with {len(gages2_assembled)} GAGES2 gauges")

# Prepare datasets that have gauge_id as index but also contain usgs_gauge_id column
index_based_datasets = [
    (cara_attrs, "Caravan"),
    (cara_HA_attrs, "HydroAtlas"),
    (cara_geo_attrs, "Geographic"),
    (cara_giw, "GIW"),
    (cara_niw, "NWI"),
    (cara_agemajor, "Age Major"),
    (cara_ageweighted, "Age Weighted"),
    (cara_ecoregion, "Ecoregion"),
]

# Join datasets with gauge_id as index
for attr_df, attr_name in index_based_datasets:
    print(f"Joining {attr_name} attributes...")

    # Create a copy with usgs_gauge_id as index
    df_copy = attr_df.copy().reset_index()

    # Check for duplicate usgs_gauge_id
    if df_copy["usgs_gauge_id"].duplicated().any():
        print(
            f"Warning: {df_copy['usgs_gauge_id'].duplicated().sum()} duplicate usgs_gauge_id in {attr_name}"
        )
        # Keep first occurrence of each usgs_gauge_id
        df_copy = df_copy.drop_duplicates(subset=["usgs_gauge_id"])

    df_copy.set_index("usgs_gauge_id", inplace=True)

    # Remove the original gauge_id column to avoid confusion
    if "gauge_id" in df_copy.columns:
        df_copy.drop(columns=["gauge_id"], inplace=True)

    # Find overlapping columns
    overlap_cols = list(set(df_copy.columns) & set(gages2_assembled.columns))

    # If overlapping columns exist, temporarily rename them
    temp_rename_dict = {col: f"{col}_temp" for col in overlap_cols}
    if temp_rename_dict:
        df_copy.rename(columns=temp_rename_dict, inplace=True)
        gages2_assembled = gages2_assembled.join(df_copy, how="left")

        # For each overlapping column, use gages2_attrs values where available
        for orig_col, temp_col in temp_rename_dict.items():
            gages2_assembled[orig_col] = gages2_assembled[orig_col].combine_first(
                gages2_assembled[temp_col]
            )
            gages2_assembled.drop(columns=[temp_col], inplace=True)
    else:
        # No overlapping columns, do a regular join
        gages2_assembled = gages2_assembled.join(df_copy, how="left")

# Join datasets that already have usgs_gauge_id as column
column_based_datasets = [
    (hammond_clim_attrs, "Hammond Climate"),
    (morph_attrs, "Morphological"),
]

for attr_df, attr_name in column_based_datasets:
    print(f"Joining {attr_name} attributes...")

    # Create a copy with usgs_gauge_id as index
    df_copy = attr_df.copy()

    # Check for duplicate usgs_gauge_id
    if df_copy["usgs_gauge_id"].duplicated().any():
        print(
            f"Warning: {df_copy['usgs_gauge_id'].duplicated().sum()} duplicate usgs_gauge_id in {attr_name}"
        )
        # Keep first occurrence of each usgs_gauge_id
        df_copy = df_copy.drop_duplicates(subset=["usgs_gauge_id"])

    df_copy.set_index("usgs_gauge_id", inplace=True)

    # Find overlapping columns
    overlap_cols = list(set(df_copy.columns) & set(gages2_assembled.columns))

    # If overlapping columns exist, temporarily rename them
    temp_rename_dict = {col: f"{col}_temp" for col in overlap_cols}
    if temp_rename_dict:
        df_copy.rename(columns=temp_rename_dict, inplace=True)
        gages2_assembled = gages2_assembled.join(df_copy, how="left")

        # For each overlapping column, use gages2_attrs values where available
        for orig_col, temp_col in temp_rename_dict.items():
            gages2_assembled[orig_col] = gages2_assembled[orig_col].combine_first(
                gages2_assembled[temp_col]
            )
            gages2_assembled.drop(columns=[temp_col], inplace=True)
    else:
        # No overlapping columns, do a regular join
        gages2_assembled = gages2_assembled.join(df_copy, how="left")

# Report final assembled attributes
print("\nFinal GAGES2-based assembled attributes:")
print(f"Number of gauges: {len(gages2_assembled)}")
print(f"Number of attributes: {gages2_assembled.shape[1]}")

# Save the assembled attributes
output_file_g2 = os.path.join(assembled_attrs_dir, "attrs_gages2_based_20250517.csv")
gages2_assembled.to_csv(output_file_g2)
print(f"Saved GAGES2-based assembled attributes to {output_file_g2}")

# %%
# Display first few rows of both datasets to verify
print("\nFirst few rows of Caravan-based assembly:")
print(assembled_attrs.head(2))

print("\nFirst few rows of GAGES2-based assembly:")
print(gages2_assembled.head(2))

# %%
