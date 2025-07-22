# %%
import os
import pandas as pd
import numpy as np

# %%
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"

#######################################################
# Get GAGES2 climate attributes
#######################################################
gridmet_dir = os.path.join(data_dir, "GAGES2_gridMET")
clim_attrs_file = os.path.join(gridmet_dir, "clim_attrs_gridmet_biascorr.csv")
clim_attrs = pd.read_csv(clim_attrs_file)
clim_attrs.head()

clim_attrs["gauge_id"] = "gages2_" + clim_attrs["usgs_gauge_id"].astype(str).str.zfill(
    8
)
clim_attrs.set_index("gauge_id", inplace=True)
clim_attrs.head()
# %%
#######################################################
# Get Caravan landscape attributes
#######################################################
caravan_attrs_file = os.path.join(data_dir, "Caravan_attrs_gages2", "attributes.csv")
caravan_attrs = pd.read_csv(caravan_attrs_file)
caravan_attrs.set_index("gauge_id", inplace=True)
caravan_attrs.head()

# %%
caravan_attrs_clim = caravan_attrs.merge(
    clim_attrs, left_index=True, right_index=True, how="left"
)
caravan_attrs_clim.head()
# # %%
# caravan_attrs_clim.to_csv(
#     os.path.join(data_dir, "Caravan_attrs_gages2", "attributes_clim.csv")
# )

# %%
#######################################################
# Get geology and wetland attributes
#######################################################
geo_wet_file = os.path.join(
    data_dir, "derived_attrs", "assembled_RA", "attrs_Holt2025_gages2_not_cara.csv"
)
geo_wet_attrs = pd.read_csv(geo_wet_file)
geo_wet_attrs.set_index("gauge_id", inplace=True)
geo_wet_attrs.head()

# %%
caravan_attrs_clim_geo_wet = caravan_attrs_clim.merge(
    geo_wet_attrs, left_index=True, right_index=True, how="left"
)
caravan_attrs_clim_geo_wet.head()
# %%
caravan_attrs_clim_geo_wet.to_csv(
    os.path.join(data_dir, "Caravan_attrs_gages2", "attributes_clim_geo_wet.csv")
)
# %%
#######################################################
# Filter out the gages that had enough streamflow records to claculate signatures from observed data
#######################################################
gages2_sigs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\gages2_20250608\out_calc_All_custom_filt_qc_snow.csv"
gages2_sigs = pd.read_csv(gages2_sigs_file)
gages2_sigs.head()

gages2_sigs["gauge_id"] = "gages2_" + gages2_sigs["gauge_id"].astype(str).str.zfill(8)
gages2_sigs.set_index("gauge_id", inplace=True)
gages2_sigs.head()

# %% Drop if "geol_weighted_ave_age_ma" is NaN
caravan_attrs_clim_geo_wet = caravan_attrs_clim_geo_wet[
    ~caravan_attrs_clim_geo_wet["geol_weighted_ave_age_ma"].isna()
]
caravan_attrs_clim_geo_wet.head()
# %%
caravan_attrs_to_pred = caravan_attrs_clim_geo_wet[
    ~caravan_attrs_clim_geo_wet.index.isin(gages2_sigs.index)
]
caravan_attrs_to_pred.head()
print(
    f"There are {len(caravan_attrs_to_pred)} gages to predict, out of {len(caravan_attrs_clim_geo_wet)} Caravan gages"
)
# %%
caravan_attrs_to_pred.to_csv(
    os.path.join(data_dir, "Caravan_attrs_gages2", "attributes_to_pred.csv")
)
# %%
