# %%
import os
import pandas as pd
import numpy as np

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"

gridmet_sigs_dir = "gages2_20250608"
caravan_sigs_dir = "caravan_us_20250525"
sigs_filename = "out_calc_All_custom.csv"
gridmet_sigs_file = os.path.join(sig_dir, gridmet_sigs_dir, sigs_filename)
caravan_sigs_file = os.path.join(sig_dir, caravan_sigs_dir, sigs_filename)

# %%
gridmet_sigs = pd.read_csv(gridmet_sigs_file)
gridmet_sigs["gauge_id"] = gridmet_sigs["gauge_id"].astype(str)
caravan_sigs = pd.read_csv(caravan_sigs_file)
caravan_sigs["gauge_num"] = caravan_sigs["gauge_num"].astype(str).str.zfill(8)

# %%
attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
gages2_attrs = pd.read_csv(attrs_file)
gages2_attrs["gauge_id"] = gages2_attrs["STAID"].astype(str).str.zfill(8)

# %%
qa_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\caravan_datacheck\gages2_summary.csv"
qa_gages2 = pd.read_csv(qa_file)
qa_gages2["gauge_id"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)


# %% (1) Get GAGES-II gauges that are not overlapping with caravan
gages2_attrs_not_in_caravan = gages2_attrs[
    ~gages2_attrs["gauge_id"].isin(caravan_sigs["gauge_num"])
]
print("Original number of GAGES-II gauges: \n", len(gages2_attrs))
print(
    f"GAGES-II gauges not overlapping with caravan:\n {len(gages2_attrs_not_in_caravan)} ({len(gages2_attrs_not_in_caravan) / len(gages2_attrs) * 100:.2f}%)"
)


# %% (2) Get GAGES-II gauges with good data quality based on QA results

##################################################################
# QUALITY CONTROL THRESHOLDS

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
qa_gages2["start_date"] = pd.to_datetime(qa_gages2["start_date"])
qa_gages2["end_date"] = pd.to_datetime(qa_gages2["end_date"])
qa_gages2["duration_yr"] = (
    qa_gages2["end_date"] - qa_gages2["start_date"]
).dt.days / 365
qa_gages2["qf_duration"] = qa_gages2["duration_yr"] > duration_thresh
print(
    f"{qa_gages2['qf_duration'].sum()} gauges passed the duration criteria > {duration_thresh} years"
)

# Filer by the nan fraction in the available (non-NaN) data record, use "subset_nan_fraction_thresh"
qa_gages2["qf_subset_nan_fraction"] = (
    qa_gages2["subset_nan_fraction"] < subset_nan_fraction_thresh
)
print(
    f"{qa_gages2['qf_subset_nan_fraction'].sum()} gauges passed the nan fraction criteria < {subset_nan_fraction_thresh}"
)

# Combine all the criteria
qa_gages2["qf_overall"] = qa_gages2["qf_subset_nan_fraction"] & qa_gages2["qf_duration"]

print(
    f"{qa_gages2['qf_overall'].sum()} gauges passed the criteria ({qa_gages2['qf_overall'].sum() / len(qa_gages2['qf_overall']) * 100:.1f} percent)"
)

# %% Merge with signature data
# Get the filtered dataset
gages2_attrs_not_in_caravan["gauge_id"] = (
    gages2_attrs_not_in_caravan["gauge_id"].astype(str).str.zfill(8)
)
qa_gages2["gauge_id"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)
sigs_gages2_qf = gages2_attrs_not_in_caravan.merge(qa_gages2, on="gauge_id")
sigs_gages2_filt = sigs_gages2_qf[sigs_gages2_qf["qf_overall"]]

print(
    f"Original number of GAGES-II gauges not in Caravan: \n {len(gages2_attrs_not_in_caravan)}"
)
print(
    f"{len(sigs_gages2_filt)} GAGES-II gauges left after Quality Assessment ({len(sigs_gages2_filt) / len(gages2_attrs_not_in_caravan) * 100:.1f}%)"
)
print(
    f"{len(sigs_gages2_qf) - len(sigs_gages2_filt)} ({(len(sigs_gages2_qf) - len(sigs_gages2_filt)) / len(sigs_gages2_qf) * 100:.1f}%) GAGES-II gauges did not pass the quality control"
)

# %% (3) Filter out overland flow signatures where significant snow
# %% (-) Filter out signatures where watershed area error is large
#  --- I do not need this for GAGES-II because
# I do not have Caravan-based area calculation to compare with
