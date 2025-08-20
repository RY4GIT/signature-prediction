# %% Get attribute sets for RF predictions (Wu signatures)

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# %% ____________________________________________________________
# Config

shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
cara_attrs_dir = os.path.join(shared_drive, "data", "Caravan1.4", "attributes")
derived_attrs_dir = os.path.join(shared_drive, "data", "derived_attrs", "assembled_RA")
gages2_attrs_dir = os.path.join(shared_drive, "data", "GAGES2", "GAGES_II_attrs")
sigs_dir = os.path.join(
    shared_drive,
    "out",
    "signatures",
    "Wu_sigs_20250812",
    "out_sigEvent_cara_gg2_rf_train.csv",
)
out_dir = derived_attrs_dir
fig_dir = os.path.join(derived_attrs_dir, "figs")
# %% ____________________________________________________________
# Get the derived attributes
# This file tries to get
# (A) the subset of Caravan(HYSETS) + GAGES2 overlapping gauges that were not predicted because of the bad data quality
# (B) the subset of Caravan(HYSETS) gauges, that were not predicted because not overlapping with GAGES2
# Caravan(Camels) should have a good data quality (except area error), so no filtering was applied

# Get the derived attributes of Caravan+GAGES2
file_name = "attrs_cara_gages2_etc_20250517+cluster"
attrs_file = os.path.join(derived_attrs_dir, file_name + ".csv")
attrs = pd.read_csv(attrs_file, index_col="gauge_id")
attrs["gauge_num"] = attrs["gauge_id"].str.split("_").str[1]

# Get the attributes of Caravan
cara_attrs_file = os.path.join(derived_attrs_dir, "attrs_caravan_us_epa.csv")
cara_attrs = pd.read_csv(cara_attrs_file, index_col="gauge_id")
cara_attrs["gauge_num"] = cara_attrs["gauge_id"].str.split("_").str[1]

# Get the attributes of CAMELS
camels_attrs_file = os.path.join(derived_attrs_dir, "attrs_camels.csv")
camels_attrs = pd.read_csv(camels_attrs_file, index_col="gauge_id")

# Get the attributes of GAGES2
gages2_attrs_file = os.path.join(gages2_attrs_dir, "gagesII_sept30_2011_concat.csv")
gages2_attrs = pd.read_csv(gages2_attrs_file)
gages2_attrs["usgs_gauge_id"] = gages2_attrs["STAID"].astype(str).str.zfill(8)
gages2_attrs["gauge_id"] = "gages2_" + gages2_attrs["usgs_gauge_id"]
gages2_attrs = gages2_attrs.set_index("gauge_id")

# Get the signatures
sig = pd.read_csv(sigs_dir, index_col="gauge_id")

print(f"There are {len(attrs)} Caravan+GAGES2 attribute file")
print(f"There are {len(cara_attrs)} Caravan gauges")
print(f"There are {len(camels_attrs)} CAMELS gauges")
print(f"There are {len(gages2_attrs)} GAGES2 gauges")
print(f"There are {len(sig)} Wu signatures")

# %%
# Mask overland flow signature calculated for snowy area
frac_snow_thresh = 0.2  # in fraction (-)

# Drop the gauges with drainage area estimation error > 25%
area_err_thresh = 0.25  # in fraction (-)

# From attrs, drop where SNOW_FRAC_PRECIP > frac_snow_thresh and area_error > area_err_thresh
len_before = len(attrs)
attrs["area_err"] = abs((attrs["area"] - attrs["DRAIN_SQKM"]) / attrs["DRAIN_SQKM"])
attrs_goodq = attrs[
    (
        (attrs["SNOW_FRAC_PRECIP"] < frac_snow_thresh)
        | (attrs["SNOW_FRAC_PRECIP"].isna())
    )
    & ((attrs["area_err"] < area_err_thresh) | (attrs["area_err"].isna()))
]
len_after = len(attrs_goodq)
print(
    f"There are {len(attrs_goodq)} Caravan+GAGES2 overlapping gauges that passed the quality control"
)
print(f"Removed {len_before - len_after} gauges")


# %% ######################################################
# (A) Get the subset of Caravan + GAGES2 overlapping gauges
# that were not predicted because of the bad data quality
###########################################################
cara_gg2_overlap = attrs_goodq.dropna(subset=["DRAIN_SQKM"])


print(f"There are {len(cara_gg2_overlap)} Caravan+GAGES2 overlapping gauges")

# Get the gauges that are in the signatures but not in the Caravan+GAGES2 overlapping gauges
cara_gg2_overlap_not_predicted = cara_gg2_overlap[
    ~cara_gg2_overlap.index.isin(sig.index)
]
print(
    f"There are {len(cara_gg2_overlap_not_predicted)} gauges that are in the signatures but not predicted because of bad data quality or lack of climate data"
)

cara_gg2_overlap_not_predicted.to_csv(
    os.path.join(out_dir, file_name + "_forWuRF_cara_gg2_baddata.csv")
)

# %%
# ######################################################
# (B) the subset of Caravan(HYSETS) gauges,
# that were not predicted because of bad quality & not overlapping with GAGES2
###########################################################

# Get the hys_gauges_not_pred that are NOT overlapping with GAGES2
hys_not_predicted = attrs_goodq[attrs_goodq["DRAIN_SQKM"].isna()]

print(
    f"There are {len(hys_not_predicted)} gauges that were not predicted because of bad data quality and not overlapping with GAGES2"
)
hys_not_predicted.to_csv(os.path.join(out_dir, file_name + "_forWuRF_hys_only.csv"))


# %%
# ######################################################
# (C) the subset of GAGES2 gages, because there were no Caravan gages
# (count the numbers for now)
# ######################################################
gages2_attrs_not_in_cara = gages2_attrs[~gages2_attrs.index.isin(attrs_goodq.index)]
print(f"There are {len(gages2_attrs_not_in_cara)} GAGES2 gages that are not in Caravan")

gages2_in_cara = gages2_attrs[
    gages2_attrs["usgs_gauge_id"].isin(attrs["usgs_gauge_id"])
]
print(f"There are {len(gages2_in_cara)} GAGES2 gages that are in Caravan")

# %% ###########################################################
# (D) Need to replace the column name "area" with "DRAIN_SQKM"
# Because the RF model only takes the column names trained for
################################################################

# Create a copy of the dataframe to avoid modifying the original
hys_not_predicted_psudo_name = hys_not_predicted.copy()

attr_pairs = [
    ("ele_mt_sav", "ELEV_MEAN_M_BASIN", "Elevation"),
    ("area", "DRAIN_SQKM", "Area"),
    ("slp_dg_sav", "SLOPE_DEG_x10", "Slope"),
    ("for_pc_sse", "FORESTNLCD06", "Forest cover"),
    ("crp_pc_sse", "CROPSNLCD06", "Crop cover"),
    ("pst_pc_sse", "PASTURENLCD06", "Pasture"),
    ("ire_pc_sse", "PCT_IRRIG_AG", "Irrigation"),
    ("prm_pc_sse", "SNOWICENLCD06", "Permanent snow/ice"),
    ("pac_pc_sse", "PADCAT1_AND_2", "Protected areas"),
    ("cly_pc_sav", "CLAYAVE", "Clay"),
    ("slt_pc_sav", "SILTAVE", "Silt"),
    ("ppd_pk_sav", "PDEN_2000_BLOCK", "Population density"),
    ("p_mean", "P_mm_day", "Precipitation"),
    ("pet_mean_FAO_PM", "PET_mm_day", "PET"),
    ("aridity_FAO_PM", "ARIDITY_GAGES2", "Aridity"),
    ("frac_snow", "SNOW_FRAC_PRECIP", "Snow fraction"),
]
for i, (cara_varname, gages2_varname, title) in enumerate(attr_pairs):
    # Only drop gages2_varname if it exists in the dataframe
    if gages2_varname in hys_not_predicted_psudo_name.columns:
        hys_not_predicted_psudo_name = hys_not_predicted_psudo_name.drop(
            columns=[gages2_varname]
        )

    # Only rename if cara_varname exists
    if cara_varname in hys_not_predicted_psudo_name.columns:
        hys_not_predicted_psudo_name.rename(
            columns={cara_varname: gages2_varname}, inplace=True
        )
        print(f"Column name {cara_varname} is replaced with {gages2_varname}")
    else:
        print(f"Warning: Column {cara_varname} not found in dataframe")


selected_attrs = [
    "ELEV_MEAN_M_BASIN",
    "DRAIN_SQKM",
    "SLOPE_DEG_x10",
    "FORESTNLCD06",
    "CROPSNLCD06",
    "PASTURENLCD06",
    "PCT_IRRIG_AG",
    "SNOWICENLCD06",
    "PADCAT1_AND_2",
    "isowet_areafrac",
    "CLAYAVE",
    "SILTAVE",
    "soc_th_sav",
    "kar_pc_sse",
    "geol_weighted_ave_age_ma",
    "PDEN_2000_BLOCK",
    "gdp_ud_sav",
    "hdi_ix_sav",
    "P_mm_day",
    "PET_mm_day",
    "ARIDITY_GAGES2",
    "SNOW_FRAC_PRECIP",
    "seasonality_FAO_PM",
    "high_prec_freq",
    "low_prec_freq",
    "low_prec_dur",
]
hys_not_predicted_psudo_name[selected_attrs].to_csv(
    os.path.join(out_dir, file_name + "_forWuRF_hys_only_psudo_name.csv")
)

# %%
