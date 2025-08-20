# %%
import os
import pandas as pd
import numpy as np

# %% ####################################
# LOAD DATA
########################################
shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow"
data_dir = os.path.join(shared_drive, "RAraki", "data")
out_dir = os.path.join(data_dir, "Caravan_attrs_gages2")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
file_name = "attributes_to_pred"
attrs = pd.read_csv(os.path.join(out_dir, file_name + ".csv"))

# %%
sig_dir = os.path.join(shared_drive, "RAraki", "out", "signatures", "Wu_sigs_20250812")
sig = pd.read_csv(os.path.join(sig_dir, "out_sigEvent_cara_gg2.csv"))
sig.set_index("gauge_id", inplace=True)
sig_gages2 = sig[sig["data_name"] == "gages2"]
sig_gages2.head()

# %%
attrs_to_pred = attrs[~attrs["gauge_id"].isin(sig_gages2.index)]
print(f"There are {len(attrs_to_pred)} attributes not calculated for Wu signatures")
attrs_to_pred
# %%
attrs_to_pred.set_index("gauge_id", inplace=True)
attrs_to_pred.head()
# %% ####################################
# USE EQUIVALENTs
########################################
# Create a list of all attribute pairs to plot
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
    ("p_mean_mm_gridmet", "P_mm_day", "Precipitation"),
    ("pet_gridmet_biascorr", "PET_mm_day", "PET"),
    ("aridity_gridmet_biascorr", "ARIDITY_GAGES2", "Aridity"),
    ("frac_snow_gridmet", "SNOW_FRAC_PRECIP", "Snow fraction"),
    ("seasonality_gridmet", "seasonality_FAO_PM", "Seasonality"),
    ("high_prec_freq_gridmet", "high_prec_freq", "High Precipitation Frequency"),
    ("low_prec_freq_gridmet", "low_prec_freq", "Low Precipitation Frequency"),
    ("low_precip_dur_gridmet", "low_prec_dur", "Low Precipitation Duration"),
]


# Create a copy of the dataframe to avoid modifying the original
attrs_psudo_name = attrs_to_pred.copy()

for i, (cara_varname, gages2_varname, title) in enumerate(attr_pairs):
    # Only drop gages2_varname if it exists in the dataframe
    if gages2_varname in attrs_psudo_name.columns:
        attrs_psudo_name = attrs_psudo_name.drop(columns=[gages2_varname])

    # Only rename if cara_varname exists
    if cara_varname in attrs_psudo_name.columns:
        attrs_psudo_name.rename(columns={cara_varname: gages2_varname}, inplace=True)
        print(f"Column name {cara_varname} is replaced with {gages2_varname}")
    else:
        print(f"Warning: Column {cara_varname} not found in dataframe")

# %%
selected_attrs = [
    "ELEV_MEAN_M_BASIN",
    "DRAIN_SQKM",
    "SLOPE_DEG_x10",
    "FORESTNLCD06",
    "CROPSNLCD06",
    "PASTURENLCD06",
    "PCT_IRRIG_AG",
    "PADCAT1_AND_2",
    "isowet_areafrac",
    "CLAYAVE",
    "SILTAVE",
    "soc_th_sav",
    "kar_pc_sse",
    "geol_weighted_ave_age_ma",
    "PDEN_2000_BLOCK",
    "P_mm_day",
    "PET_mm_day",
    "ARIDITY_GAGES2",
    "SNOW_FRAC_PRECIP",
    "seasonality_FAO_PM",
    "high_prec_freq",
    "low_prec_freq",
    "low_prec_dur",
]
attrs_psudo_name[selected_attrs].to_csv(
    os.path.join(out_dir, file_name + "_forWuRF_psudo_name.csv")
)

# %%
