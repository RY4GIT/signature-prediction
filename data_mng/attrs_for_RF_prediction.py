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
attrs_file = os.path.join(
    derived_attrs_dir, "attrs_cara_and_gages2+climate+morph+padcat+cluster.csv"
)
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

print(f"There are {len(attrs)} Caravan+GAGES2 gauges")
print(f"There are {len(cara_attrs)} Caravan gauges")
print(f"There are {len(camels_attrs)} CAMELS gauges")
print(f"There are {len(gages2_attrs)} GAGES2 gauges")
print(f"There are {len(qa_hys)} HYSETS gauges")
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

print(
    f"{qa_hys['qf_overall'].sum()} gauges passed the criteria ({qa_hys['qf_overall'].sum() / len(qa_hys['qf_overall']) * 100:.1f} percent)"
)
print(
    f"There are {len(qa_hys[qa_hys['qf_overall'] == False])} gauges ({len(qa_hys[qa_hys['qf_overall'] == False]) / len(qa_hys) * 100:.1f} percent) that were not predicted because of the bad data quality"
)


# %%  Join the attributes with the quality control statistics
attrs = attrs.join(qa_hys, how="left", rsuffix="_qa")

print(len(attrs))

# Get the gauge_id of the gauges that were not predicted because of the bad data quality
hys_gauges_not_pred = attrs[attrs["qf_overall"] == False]

print(
    f"There are {len(hys_gauges_not_pred)} gauges that were not predicted because of the bad data quality"
)

# %% Make sure hys_gauges_not_pred do not include any gauge_id that is in camels_attrs
# Remove any gauge_id from hys_gauges_not_pred that exists in camels_attrs
hys_gauges_not_pred = hys_gauges_not_pred[
    ~hys_gauges_not_pred.index.isin(camels_attrs.index)
]


# Count gauges removed in each filtering step
n_camels_removed = len(
    hys_gauges_not_pred[hys_gauges_not_pred.index.isin(camels_attrs.index)]
)

n_remaining = len(hys_gauges_not_pred)

print(
    f"Summary of gauge filtering:"
    f"\n- Removed {n_camels_removed} CAMELS gauges"
    f"\n- {n_remaining} gauges remain that were not predicted due to bad data quality"
)

# %% ######################################################
# (A) Get the subset of Caravan(HYSETS) + GAGES2 overlapping gauges
# that were not predicted because of the bad data quality
###########################################################

# Get the hys_gauges_not_pred that are overlapping with GAGES2
hys_gages_not_pred_in_gages2 = hys_gauges_not_pred[
    ~hys_gauges_not_pred["DRAIN_SQKM"].isna()
]
# Make sure the area error is not too high
hys_gages_not_pred_in_gages2["area_err"] = abs(
    (hys_gages_not_pred_in_gages2["area"] - hys_gages_not_pred_in_gages2["DRAIN_SQKM"])
    / hys_gages_not_pred_in_gages2["DRAIN_SQKM"]
)
hys_gages_not_pred_in_gages2 = hys_gages_not_pred_in_gages2[
    (hys_gages_not_pred_in_gages2["area_err"] < area_err_thresh)
]
n_area_err_removed = len(
    hys_gages_not_pred_in_gages2[
        hys_gages_not_pred_in_gages2["area_err"] > area_err_thresh
    ]
)
print(f"Out of {len(hys_gauges_not_pred)} data with bad quality, ")
print(
    f"There are {len(hys_gages_not_pred_in_gages2)} gauges that were not predicted because of bad data quality but overlapping with GAGES2"
)
print(f"- Removed {n_area_err_removed} gauges with area error > {area_err_thresh}")

hys_gages_not_pred_in_gages2.to_csv(
    os.path.join(out_dir, "attrs_for_RF_pred_baddata_hys_gages2.csv")
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
    f"There are {len(hys_gages_not_pred_not_in_gages2)} gauges that were not predicted because of bad data quality but overlapping with GAGES2"
)
hys_gages_not_pred_not_in_gages2.to_csv(
    os.path.join(out_dir, "attrs_for_RF_pred_baddata_hys_not_gages2.csv")
)

# %% ######################################################
# Check some Caravan-GAGES2 equivalent attributes
# ######################################################


# Create a list of all attribute pairs to plot
attr_pairs = [
    ("sgr_dk_sav", "SLOPE_PCT", "Slope"),
    ("soc_th_sav", "OMAVE", "Soil organic matter"),
    ("hdi_ix_sav", "FRAGUN_BASIN", "Development index"),
    ("pet_mean", "PET_mm_day", "PET"),
    ("aridity", "ARIDITY_GAGES2", "Aridity"),
    ("seasonality", "PRECIP_SEAS_IND", "Seasonality"),
    ("area", "DRAIN_SQKM", "Area"),
    ("ele_mt_sav", "ELEV_MEAN_M_BASIN", "Elevation"),
    ("for_pc_sse", "FORESTNLCD06", "Forest cover"),
    ("crp_pc_sse", "CROPSNLCD06", "Crop cover"),
    ("pst_pc_sse", "PASTURENLCD06", "Pasture"),
    ("prm_pc_sse", "SNOWICENLCD06", "Permanent snow/ice"),
    ("ire_pc_sse", "PCT_IRRIG_AG", "Irrigation"),
    ("pac_pc_sse", "PADCAT1_AND_2", "Protected areas"),
    ("cly_pc_sav", "CLAYAVE", "Clay"),
    ("slt_pc_sav", "SILTAVE", "Silt"),
    ("p_mean", "P_mm_day", "Precipitation"),
    ("frac_snow", "SNOW_PCT_PRECIP", "Snow fraction"),
    ("ppd_pk_sav", "PDEN_2000_BLOCK", "Population density"),
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

    if gages2_varname == "SNOW_PCT_PRECIP":
        gages2_var = gages2_var / 100

    if gages2_varname == "SLOPE_PCT":
        gages2_var = gages2_var / 100 * 1000
        # SLOPE_PCT / 100 (conversion factor to fraction) * 1000 (rise or drop per 1000m) ~ sgr_dk_sav

    if gages2_varname == "OMAVE":
        cara_var = cara_var * 10000000 / 1500 / (100 - 10) / 30

    axs[i].scatter(cara_var, gages2_var, s=1, alpha=0.5)

    # Add 1:1 line
    lims = [
        min(min(cara_var), min(gages2_var)),
        max(max(cara_var), max(gages2_var)),
    ]
    axs[i].plot(lims, lims, "k--", alpha=0.5, zorder=0)

    axs[i].set_title(title)
    axs[i].set_xlabel(f"{cara_varname}")
    axs[i].set_ylabel(f"{gages2_varname}")

    # Show median values
    axs[i].text(
        0.05,
        0.95,
        f"Caravan: {cara_var.median():.2f}\nGAGES2: {gages2_var.median():.2f}",
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

# %%


# %%


# %%

# %%

# %%
