# %% Post proces signatures calculated for Caravan gages

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

# Get the attributes of Caravan
cara_attrs_file = os.path.join(derived_attrs_dir, "attrs_caravan_us_epa.csv")
cara_attrs = pd.read_csv(cara_attrs_file, index_col="gauge_id")

# Get the attributes of CAMELS
camels_attrs_file = os.path.join(derived_attrs_dir, "attrs_camels.csv")
camels_attrs = pd.read_csv(camels_attrs_file, index_col="gauge_id")

# Get the attributes of GAGES2
gages2_attrs_file = os.path.join(gages2_attrs_dir, "gagesII_sept30_2011_concat.csv")
gages2_attrs = pd.read_csv(gages2_attrs_file)
gages2_attrs["usgs_gauge_id"] = gages2_attrs["STAID"].astype(str).str.zfill(8)
gages2_attrs = gages2_attrs.set_index("usgs_gauge_id")

# Get quality control statistics of HYSETS
hys_qa_file = os.path.join(
    shared_drive, "out", "caravan_datacheck", "hysets_summary.csv"
)
qa_hys = pd.read_csv(hys_qa_file, index_col="gauge_id")

print(f"There are {len(attrs)} Caravan+GAGES2 attribute file")
print(f"There are {len(cara_attrs)} Caravan gauges")
print(f"There are {len(camels_attrs)} CAMELS gauges")
print(f"There are {len(gages2_attrs)} GAGES2 gauges")
print(f"There are {len(qa_hys)} HYSETS gauges")

# %%
length_before = len(attrs)
attrs = attrs[attrs["country"] == "United States of America"]
print(
    f"There are {len(attrs)} Caravan+GAGES2 gauges after dropping {length_before - len(attrs)} gauges not in the US"
)

# Drop HYSETS gages with the same gauge_id as CAMELS
camels_attrs["usgs_gauge_id"] = camels_attrs.index.str.split("_").str[1].str.zfill(8)
attrs["usgs_gauge_id"] = attrs.index.str.split("_").str[1].str.zfill(8)
attrs["hysets"] = attrs.index.str.startswith("hysets_")
overlap_idx = (
    attrs["usgs_gauge_id"].isin(camels_attrs["usgs_gauge_id"]) & attrs["hysets"]
)
attrs = attrs[~overlap_idx].copy()
print(
    f"There are {len(attrs)} Caravan+GAGES2 gauges after dropping {overlap_idx.sum()} ovrelapping CAMELS gauges"
)

# %%
# Drop data that are not in the CONUS (use the gage_lat and gage_lon)
conus_bbox = (20, -125, 50, -65)
length_before = len(attrs)
attrs = attrs[attrs["gauge_lat"] > conus_bbox[0]]
attrs = attrs[attrs["gauge_lon"] > conus_bbox[1]]
attrs = attrs[attrs["gauge_lat"] < conus_bbox[2]]
attrs = attrs[attrs["gauge_lon"] < conus_bbox[3]]
print(
    f"There are {len(attrs)} Caravan+GAGES2 gauges after dropping {length_before - len(attrs)} gauges not in CONUS based on lat/lon"
)


# %%
##################################################################
# QUALITY CONTROL THRESHOLDS (same ones used in postprocess_caravan_sigs_for_RF.py)

# Filter signatures by duration of the record
duration_thresh = 5  # in years

# Filer by the nan fraction in the available (non-NaN) data record
subset_nan_fraction_thresh = 0.3  # in fraction (-)

# Mask overland flow signature calculated for snowy area
frac_snow_thresh = 0.2  # in fraction (-)

# Drop the gauges with drainage area estimation error > 25%
area_err_thresh = 0.25  # in fraction (-)
##################################################################

# Filter signatures by duration of the record, use "duration_thresh"
qa_hys["start_date"] = pd.to_datetime(qa_hys["start_date"])
qa_hys["end_date"] = pd.to_datetime(qa_hys["end_date"])
qa_hys["duration_yr"] = (qa_hys["end_date"] - qa_hys["start_date"]).dt.days / 365
qa_hys["qf_duration"] = qa_hys["duration_yr"] > duration_thresh

# Filer by the nan fraction in the available (non-NaN) data record, use "subset_nan_fraction_thresh"
qa_hys["qf_subset_nan_fraction"] = (
    qa_hys["subset_nan_fraction"] < subset_nan_fraction_thresh
)

# Combine all the criteria
qa_hys["qf_overall"] = qa_hys["qf_subset_nan_fraction"] & qa_hys["qf_duration"]

# Replace qf_overall to True where index starts from "camels_"
qa_hys.loc[qa_hys.index.str.startswith("camels_"), "qf_overall"] = True

# print(
#     f"Out of {len(qa_hys)} Caravan(HYSETS+CAMELS) gauges, {qa_hys['qf_overall'].sum()} passed the criteria ({qa_hys['qf_overall'].sum() / len(qa_hys['qf_overall']) * 100:.1f} percent)"
# )
# print(
#     f"There are {len(qa_hys[qa_hys['qf_overall'] == False])} gauges ({len(qa_hys[qa_hys['qf_overall'] == False]) / len(qa_hys) * 100:.1f} percent) that were not predicted because of the bad data quality"
# )


# %%  Join the attributes with the quality control statistics
attrs = attrs.join(qa_hys, how="left", rsuffix="_qa")
attrs["area_err"] = abs((attrs["area"] - attrs["DRAIN_SQKM"]) / attrs["DRAIN_SQKM"])
print(len(attrs))

# Get the gauge_id of the gauges that were not predicted because of the bad data quality
hys_gauges_not_pred = attrs[
    (attrs["qf_overall"] == False) | (attrs["area_err"] > area_err_thresh)
].copy()

print(
    f"Out of {len(attrs)} Caravan(HYSETS+CAMELS) gauges, {len(attrs) - len(hys_gauges_not_pred)} passed the criteria ({qa_hys['qf_overall'].sum() / len(qa_hys['qf_overall']) * 100:.1f} percent)"
)
print(
    f"There are {len(hys_gauges_not_pred)} gauges that were not predicted because of the bad data quality + bad area error"
)
print(
    f"because of bad quality: {len(hys_gauges_not_pred[hys_gauges_not_pred['qf_overall'] == False])}"
)
print(
    f"because of area error: {len(hys_gauges_not_pred[hys_gauges_not_pred['area_err'] > area_err_thresh])}"
)

# %% ######################################################
# (A) Get the subset of Caravan + GAGES2 overlapping gauges
# that were not predicted because of the bad data quality
###########################################################

# Get the hys_gauges_not_pred that ARE overlapping with GAGES2
hys_gages_not_pred_in_gages2 = hys_gauges_not_pred[
    ~hys_gauges_not_pred["DRAIN_SQKM"].isna()
]

# print(f"Out of {len(hys_gauges_not_pred)} data with bad quality, ")

# # Make sure the area error is not too high
# n_area_err_removed = len(
#     hys_gages_not_pred_in_gages2[
#         hys_gages_not_pred_in_gages2["area_err"] > area_err_thresh
#     ]
# )
# hys_gages_not_pred_in_gages2 = hys_gages_not_pred_in_gages2[
#     (hys_gages_not_pred_in_gages2["area_err"] < area_err_thresh)
# ]

print(
    f"There are {len(hys_gages_not_pred_in_gages2)} gauges that were not predicted because of bad data quality but overlapping with GAGES2"
)
# print(f"Removed {n_area_err_removed} gauges with area error > {area_err_thresh}")

hys_gages_not_pred_in_gages2.to_csv(
    os.path.join(out_dir, file_name + "_forRF_hys2_gg2_baddata.csv")
)
# %%
# ######################################################
# (B) the subset of Caravan(HYSETS) gauges,
# that were not predicted because of bad quality & not overlapping with GAGES2
###########################################################

# Get the hys_gauges_not_pred that are NOT overlapping with GAGES2
hys_gages_not_pred_not_in_gages2 = hys_gauges_not_pred[
    hys_gauges_not_pred["DRAIN_SQKM"].isna()
]

print(
    f"There are {len(hys_gages_not_pred_not_in_gages2)} gauges that were not predicted because of bad data quality and not overlapping with GAGES2"
)
hys_gages_not_pred_not_in_gages2.to_csv(
    os.path.join(out_dir, file_name + "_forRF_hys_only.csv")
)

# %% ######################################################
# Check the count of predicted gauges
# ######################################################

attrs_goodq = attrs[(attrs["qf_overall"] == True) | (attrs["qf_overall"].isna())]
attrs_goodq = attrs_goodq[
    (attrs_goodq["area_err"] < area_err_thresh) | (attrs_goodq["area_err"].isna())
]
# attrs_goodq = attrs_goodq[attrs_goodq["DRAIN_SQKM"].notna()]
print(f"There are {len(attrs_goodq)} gauges that have good quality")

attrs_goodq_gg2 = attrs_goodq[attrs_goodq["DRAIN_SQKM"].notna()]
print(
    f"There are {len(attrs_goodq_gg2)} gauges that have good quality and are in GAGES2"
)

attrs_goodq_hys = attrs_goodq[~attrs_goodq.index.isin(attrs_goodq_gg2.index)]
print(
    f"There are {len(attrs_goodq_hys)} gauges that have good quality and are only in Caravan"
)

# %%
sig_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20250525\out_calc_All_custom_filt_qc_snow_area.csv"
sig = pd.read_csv(sig_file)
print(f"There are {len(sig)} Caravan gages in the signature file")

# %%
# What are the differences between the predicted and the signature file?
gages_predicted_not_in_sig = attrs_goodq[~attrs_goodq.index.isin(sig["gauge_id"])]
print(
    f"There are {len(gages_predicted_not_in_sig)} gages that were deemed good quality but not in the signature file"
)
gages_predicted_not_in_sig
# %%%
sigs_not_in_pred = sig[~sig["gauge_id"].isin(attrs_goodq.index)]
print(
    f"There are {len(sigs_not_in_pred)} gages that were in the signature file but not deemed good quality"
)  # Likley they are GAGES2
sigs_not_in_pred


# %%

# %%
# ######################################################
# (C) the subset of GAGES2 gages, because there were no Caravan gages
# (count the numbers for now)
# ######################################################
gages2_attrs["usgs_gauge_id"] = gages2_attrs.index.str.zfill(8)
gages2_attrs_not_in_cara = gages2_attrs[
    ~gages2_attrs["usgs_gauge_id"].isin(attrs["usgs_gauge_id"])
]
print(f"There are {len(gages2_attrs_not_in_cara)} GAGES2 gages that are not in Caravan")

gages2_in_cara = gages2_attrs[
    gages2_attrs["usgs_gauge_id"].isin(attrs["usgs_gauge_id"])
]
print(f"There are {len(gages2_in_cara)} GAGES2 gages that are in Caravan")
# %% ######################################################
# Check some Caravan-GAGES2 equivalent attributes
# ######################################################


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
    ("p_mean", "P_mm_day", "Precipitation"),
    ("pet_mean_FAO_PM", "PET_mm_day", "PET"),
    ("aridity_FAO_PM", "ARIDITY_GAGES2", "Aridity"),
    ("frac_snow", "SNOW_FRAC_PRECIP", "Snow fraction"),
    # ("soc_th_sav", "OMAVE", "Soil organic matter"),
    # ("hdi_ix_sav", "FRAGUN_BASIN", "Development index"),
    # ("seasonality", "PRECIP_SEAS_IND", "Seasonality"),
]

# Calculate number of rows and columns needed
n_plots = len(attr_pairs)
n_cols = 6
n_rows = (n_plots + n_cols - 1) // n_cols

# Create figure and subplots
fig, axs = plt.subplots(n_rows, n_cols, figsize=(15, 2.4 * n_rows))
axs = axs.flatten()

# Plot each pair of attributes
for i, (cara_varname, gages2_varname, title) in enumerate(attr_pairs):
    cara_var = attrs[cara_varname]
    gages2_var = attrs[gages2_varname]

    # if gages2_varname == "SNOW_PCT_PRECIP":
    #     gages2_var = gages2_var / 100

    # if gages2_varname == "SLOPE_PCT":
    #     # Convert slope percent to slope degree
    #     # slope percent = rise/run * 100
    #     # slope degree = arctan(rise/run)
    #     # therefore: slope degree = arctan(slope_percent/100)
    #     gages2_var = np.arctan(gages2_var / 100) * 180 / np.pi * 10

    #     # In case of conversion from sgr_dk_sav (dm/km)to SLOPE_PCT
    #     # gages2_var = gages2_var / 100 * 1000
    #     # SLOPE_PCT / 100 (conversion factor to fraction) * 1000 (rise or drop per 1000m) ~ sgr_dk_sav

    # if gages2_varname == "OMAVE":
    #     cara_var = cara_var * 10000000 / 1500 / (100 10) / 30

    axs[i].scatter(cara_var, gages2_var, s=1, alpha=0.5)

    nan_mask = ~np.isnan(cara_var) & ~np.isnan(gages2_var)
    pearson_corr = np.corrcoef(cara_var[nan_mask], gages2_var[nan_mask])[0, 1]

    # Add 1:1 line
    lims = [
        min(min(cara_var), min(gages2_var)),
        max(max(cara_var), max(gages2_var)),
    ]
    axs[i].plot(lims, lims, "k--", alpha=0.5, zorder=0)

    axs[i].set_xlim(lims)
    axs[i].set_ylim(lims)

    axs[i].set_title(title)
    axs[i].set_xlabel(f"{cara_varname}")
    axs[i].set_ylabel(f"{gages2_varname}")

    # Show median values
    axs[i].text(
        0.05,
        0.95,
        f"Caravan: {cara_var.median():.2f}\nGAGES2: {gages2_var.median():.2f}\n$R$: {pearson_corr:.2f}",
        transform=axs[i].transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )

# Remove empty subplots if any
for i in range(len(attr_pairs), len(axs)):
    fig.delaxes(axs[i])

plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "all_attrs_comparison.png"))


# %% ###########################################################
# (D) Need to replace the column name "area" with "DRAIN_SQKM"
# Because the RF model only takes the column names trained for
################################################################

# Create a copy of the dataframe to avoid modifying the original
hys_gages_not_pred_not_in_gages2_psudo_name = hys_gages_not_pred_not_in_gages2.copy()

for i, (cara_varname, gages2_varname, title) in enumerate(attr_pairs):
    # Only drop gages2_varname if it exists in the dataframe
    if gages2_varname in hys_gages_not_pred_not_in_gages2_psudo_name.columns:
        hys_gages_not_pred_not_in_gages2_psudo_name = (
            hys_gages_not_pred_not_in_gages2_psudo_name.drop(columns=[gages2_varname])
        )

    # Only rename if cara_varname exists
    if cara_varname in hys_gages_not_pred_not_in_gages2_psudo_name.columns:
        hys_gages_not_pred_not_in_gages2_psudo_name.rename(
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
hys_gages_not_pred_not_in_gages2_psudo_name[selected_attrs].to_csv(
    os.path.join(out_dir, file_name + "_forRF_hys_only_psudo_name.csv")
)

# %%
