# %% Check gages 2 data
# - Check an overlap with hysets gauge_ids
# - Check the number of attributes

import pandas as pd
import os

# %% #########################################################################
#
# LOAD GAGES2 ATTRIBUTES
#
##############################################################################

# ____________________________________________________________
# Load attributes

gages2_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES2_attrs_Hammond\gagesII_sept30_2011_conterm.xlsx"
# Load the Excel file
xls = pd.ExcelFile(gages2_attrs_file)

# Get the sheet names
sheet_names = xls.sheet_names

# %% # ____________________________________________________________
# Concatenate all attributes

# Initialize the final DataFrame with the first sheet
sheet_name = sheet_names[0]
print(f"Processing: {sheet_name} [{0}/{len(sheet_names)}]")
gages2_attrs = pd.read_excel(
    gages2_attrs_file, sheet_name=sheet_name, index_col="STAID"
)

# Iterate over the remaining sheets and merge them on 'STAID'
for i, sheet_name in enumerate(sheet_names[1:]):
    if sheet_name == "X_Region_Names":
        # Do nothing and continue
        continue
    else:
        print(f"Processing: {sheet_name} [{i + 1}/{len(sheet_names)}]")
        _df = pd.read_excel(
            io=gages2_attrs_file, sheet_name=sheet_name, index_col="STAID"
        )
        _df["sheet_name"] = sheet_name

        # Filter out columns from `_df` that already exist in `gages2_attrs`
        columns_to_add = _df.columns.difference(gages2_attrs.columns)
        _df_filtered = _df[columns_to_add]

        gages2_attrs = gages2_attrs.join(_df_filtered, how="left")

# %%
# Now `final_df` contains all sheets concatenated horizontally on 'STAID'
print(gages2_attrs.head())


# %%
gages2_attrs["usgs_gauge_id"] = gages2_attrs.index.astype(str).str.zfill(width=8)
gages2_attrs.head()


# %%
# %% #########################################################################
#
# Hammond Climate ATTRIBUTES
#
##############################################################################
climate_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\climate_attrs_Hammond\mean_annual_climate_attributes.csv"
climate_attrs = pd.read_csv(climate_attrs_file, index_col="gageID")
climate_attrs


# %%
gages2_attrs_v2 = gages2_attrs.join(climate_attrs)

# %% #########################################################################
#
# COUNT THE OVERLAPPING GAUGES WITH HYSETS & CAMELS
#
##############################################################################

assembled_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
# ecoregion_ver = "epa"
ecoregion_ver = "hammond"
caravan_epa_filename = f"attrs_caravan_us_{ecoregion_ver}.csv"

attrs_caravan_epa = pd.read_csv(os.path.join(assembled_attrs_dir, caravan_epa_filename))


# %%
attrs_caravan_epa["usgs_gauge_id"] = (
    attrs_caravan_epa["gauge_id"].str.split("_").str[-1].str.zfill(8)
)
attrs_caravan_epa.head()

# %%
# Merge the DataFrames on 'usgs_gauge_id' with an outer join and indicator
merged_df = pd.merge(
    gages2_attrs_v2, attrs_caravan_epa, on="usgs_gauge_id", how="outer", indicator=True
)

# Identify gauges unique to gages2_attrs, unique to attrs_caravan_epa, and common
unique_to_gages2 = merged_df[merged_df["_merge"] == "left_only"][
    "usgs_gauge_id"
].tolist()
unique_to_caravan = merged_df[merged_df["_merge"] == "right_only"][
    "usgs_gauge_id"
].tolist()
common_gauges = merged_df[merged_df["_merge"] == "both"]["usgs_gauge_id"].tolist()

# Print the lengths and lists
print(f"Gauges unique to gages2_attrs: {len(unique_to_gages2)}")
print(unique_to_gages2)
print(f"Gauges unique to attrs_caravan_epa: {len(unique_to_caravan)}")
print(unique_to_caravan)
print(f"Gauges common to both: {len(common_gauges)}")
print(common_gauges)
# %%
# Return the lists (if needed in a function)
# Write results to text files
with open(
    os.path.join(assembled_attrs_dir, "caravan_vs_gages2_unique_to_gages2.txt"), "w"
) as file:
    file.write("\n".join(unique_to_gages2))

with open(
    os.path.join(assembled_attrs_dir, "caravan_vs_gages2_unique_to_caravan.txt"), "w"
) as file:
    file.write("\n".join(unique_to_caravan))

with open(
    os.path.join(assembled_attrs_dir, "caravan_vs_gages2_common_gauges.txt"), "w"
) as file:
    file.write("\n".join(common_gauges))


# Example of returning the result (if used in a function)
# return result
# %% #########################################################################
#
# CURATE AND OUTPUT THE ATTRIBUTE FILE (all GAGES2 gauges)
#
##############################################################################

gages2_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES2_attrs_Hammond"
gages2_attrs_v2.to_csv(
    os.path.join(gages2_dir, "gagesII_sept30_2011_concat+climate.csv")
)

# %% #########################################################################
#
# CURATE AND OUTPUT THE ATTRIBUTE FILE (join with eligible CAMELS and CARAVAN
# gauges, and also include Annie's attributes and ecoregions)
#
##############################################################################
common_gauges = merged_df[merged_df["_merge"] == "both"].copy()
common_gauges.set_index("gauge_id", inplace=True)
common_gauges.to_csv(
    os.path.join(assembled_attrs_dir, f"attrs_gages2+climate_{ecoregion_ver}.csv")
)

# %%
# %% #########################################################################
#
# Join the Caravan and GAGES2 attributes
#
##############################################################################
attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
ecoregion_name = "hammondv2"

caravan_filename = f"attrs_caravan_us_{ecoregion_name}.csv"
gages2_filename = f"attrs_gages2_{ecoregion_name}.csv"
out_filename = f"attrs_cara_and_gages2+climate_{ecoregion_name}.csv"

attrs_caravan = pd.read_csv(
    os.path.join(attrs_dir, caravan_filename), index_col="gauge_id"
)
attrs_gages2 = pd.read_csv(
    os.path.join(attrs_dir, gages2_filename), index_col="gauge_id"
)


merged_attrs = attrs_caravan.combine_first(attrs_gages2)
merged_attrs.to_csv(os.path.join(attrs_dir, out_filename))

# %%
