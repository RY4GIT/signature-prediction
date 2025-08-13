# %%
import numpy as np
import pandas as pd
import os

# %%
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
sig_dir = os.path.join(cloud_dir, "out", "signatures", "Wu_sigs_20250812")
local_dir = r"D:\data"

# %%
data_names = ["camels", "hysets", "gages2"]

# %% #####################################################################
# Load data
##########################################################################


def load_sig_data(data_name):
    sig_file = os.path.join(sig_dir, f"out_sigEvent_{data_name}.csv")
    df = pd.read_csv(sig_file)
    df["data_name"] = data_name
    df["gauge_num"] = df["gauge_id"].astype(str).str.split("_").str[1].str.zfill(8)

    return df


sig_camels = load_sig_data("camels")
sig_hysets = load_sig_data("hysets")
sig_gages2 = load_sig_data("gages2")


# %% #####################################################################
# Filter out by data quality for Caravan
##########################################################################

# Hysets
hys_qa_file = os.path.join(cloud_dir, "out", "caravan_datacheck", "hysets_summary.csv")
qa_hys = pd.read_csv(hys_qa_file)

# %%
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

# ____________________________________________________________
# (1) Quality control of Hysets Signautres

# Filter signatures by duration of the record, use "duration_thresh"
qa_hys["start_date"] = pd.to_datetime(qa_hys["start_date"])
qa_hys["end_date"] = pd.to_datetime(qa_hys["end_date"])
qa_hys["duration_yr"] = (qa_hys["end_date"] - qa_hys["start_date"]).dt.days / 365
qa_hys["qf_duration"] = qa_hys["duration_yr"] > duration_thresh
print(
    f"{qa_hys['qf_duration'].sum()} gauges passed the duration criteria > {duration_thresh} years"
)

# Filer by the nan fraction in the available (non-NaN) data record, use "subset_nan_fraction_thresh"
qa_hys["qf_subset_nan_fraction"] = (
    qa_hys["subset_nan_fraction"] < subset_nan_fraction_thresh
)
print(
    f"{qa_hys['qf_subset_nan_fraction'].sum()} gauges passed the nan fraction criteria < {subset_nan_fraction_thresh}"
)

# Combine all the criteria
qa_hys["qf_overall"] = qa_hys["qf_subset_nan_fraction"] & qa_hys["qf_duration"]

print(
    f"{qa_hys['qf_overall'].sum()} gauges passed the criteria ({qa_hys['qf_overall'].sum() / len(qa_hys['qf_overall']) * 100:.1f} percent)"
)

# Get the filtered dataset
sigs_hys_qf = sig_hysets.merge(qa_hys, on="gauge_id")
sigs_hys_filt = sig_hysets[sigs_hys_qf["qf_overall"]]

print(f"{len(sigs_hys_filt)} Hysets watershed left after Quality Assessment")

# %% ____________________________________________________________
# (2) Filter out the Hysets gauge_id that are overlapping with CAMELS

# If the gauge_num is in the sig_camels dataframe, then remove it from the sig_hys_filt dataframe
sigs_hys_filt = sigs_hys_filt[~sigs_hys_filt["gauge_num"].isin(sig_camels["gauge_num"])]

print(f"{len(sigs_hys_filt)} Hysets watershed left after removing CAMELS gauges")

# %% ____________________________________________________________
# (3) Mask overland flow signature calculated for snowy area, use "frac_snow_thresh"

# join camels and hysets
sigs_caravan = pd.concat([sig_camels, sigs_hys_filt])
sigs_caravan.set_index("gauge_id", inplace=True)

# Get climate attributes
attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
attrs_caravan_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_caravan_hysets.csv"),
    index_col="gauge_id",
)
attrs_caravan_camels = pd.read_csv(
    os.path.join(attrs_dir, "camels", "attributes_caravan_camels.csv"),
    index_col="gauge_id",
)
attrs_caravan_climates = pd.concat([attrs_caravan_hys, attrs_caravan_camels])

# Join climate attributes to the signatures
sigs_caravan = sigs_caravan.join(attrs_caravan_climates, how="left")
row_mask_idx = sigs_caravan["frac_snow"] > frac_snow_thresh
columns_mask = [
    "R_Pvol_RC",
    "R_Pint_RC",
]

sigs_caravan.loc[row_mask_idx, columns_mask] = np.nan

print(
    "After quality controlling the IE/SE signatures by snow, "
    + f"{(~pd.isna(sigs_caravan.R_Pvol_RC)).sum()} gauges survived ({(~pd.isna(sigs_caravan.R_Pvol_RC)).sum() / len(sigs_caravan) * 100:.1f} %)"
)

# %% ____________________________________________________________
# (4) Join GAGES2 attributes to check the area error. Drop the rows with area error > 25%

# Load GAGES2 attributes
attrs_gages2_file = os.path.join(
    cloud_dir, "data", "GAGES2", "GAGES_II_attrs", "gagesII_sept30_2011_concat.csv"
)
attrs_gages2 = pd.read_csv(attrs_gages2_file)
attrs_gages2["usgs_gauge_id"] = attrs_gages2["usgs_gauge_id"].astype(str).str.zfill(8)
sigs_caravan = sigs_caravan.merge(
    attrs_gages2, how="left", left_on="gauge_num", right_on="usgs_gauge_id"
)
print(
    f"There are {len(sigs_caravan)} gages in the GAGES2 dataset -- should be same as {len(sigs_caravan)}"
)

# %%
# Load CAMELS and Hysets attributes
attrs_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_other_hysets.csv")
)
attrs_camels = pd.read_csv(
    os.path.join(attrs_dir, "camels", "attributes_other_camels.csv")
)
# %%
attrs_caravan = pd.concat([attrs_hys, attrs_camels])
attrs_caravan["gauge_num"] = (
    attrs_caravan["gauge_id"].astype(str).str.split("_").str[1].str.zfill(8)
)
sigs_caravan = sigs_caravan.merge(
    attrs_caravan, how="left", left_on="gauge_num", right_on="gauge_num"
)

print(
    f"Caravan attributes has {len(attrs_caravan)} rows vs signatures {len(sigs_caravan)}"
)

# %%
# Drop the rows with area error > 25%
sigs_caravan["area_err"] = abs(
    (sigs_caravan["area"] - sigs_caravan["DRAIN_SQKM"]) / sigs_caravan["DRAIN_SQKM"]
)
area_err_idx = sigs_caravan[sigs_caravan["area_err"] > area_err_thresh].index

sigs_caravan_filt = sigs_caravan.drop(index=area_err_idx)

print(f"Area error threshold : (Caravan - GAGES2)/GAGES2 error > {area_err_thresh}")
print(
    f"{len(sigs_caravan_filt)} survived after area error filtering ({len(sigs_caravan_filt) / len(sigs_caravan) * 100:.1f} %)"
)
print(
    f"{len(area_err_idx)} gages were dropped due to area error ({len(area_err_idx) / len(sigs_caravan) * 100:.1f} %)"
)

# %% #####################################################################
# Filter out by data quality for GAGES2
##########################################################################
# %% Load GAGES2 data quality
qa_gages2_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\caravan_datacheck\gages2_summary.csv"
qa_gages2 = pd.read_csv(qa_gages2_file)
qa_gages2["gauge_num"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)

# %%
sigs_gages2 = sig_gages2.merge(
    attrs_gages2, how="left", left_on="gauge_num", right_on="usgs_gauge_id"
)

sigs_gages2

# %% ____________________________________________________________
#  (1) Get the bounding box of the US
us_bbox = (
    -124.848974,
    24.396308,
    -66.885444,
    49.384358,
)
mask = (
    (sigs_gages2["LAT_GAGE"] > us_bbox[1])
    & (sigs_gages2["LAT_GAGE"] < us_bbox[3])
    & (sigs_gages2["LNG_GAGE"] > us_bbox[0])
    & (sigs_gages2["LNG_GAGE"] < us_bbox[2])
)
print(len(sigs_gages2))
sigs_gages2 = sigs_gages2[mask]
print(len(sigs_gages2))

# %% # %% (2) Get GAGES-II gauges with good data quality based on QA results

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

# %% ____________________________________________________________
# Merge with signature data

# Get the filtered dataset
sigs_gages2_qf = sigs_gages2.drop(columns=["gauge_id"]).merge(
    qa_gages2, how="left", left_on="gauge_num", right_on="gauge_num"
)
sigs_gages2_filt = sigs_gages2_qf[sigs_gages2_qf["qf_overall"]].copy()


print(
    f"{len(sigs_gages2_filt)} ({len(sigs_gages2_filt) / len(sigs_gages2) * 100:.1f}%) GAGES-II gauges left after Quality Assessment"
)
print(
    f"{len(sigs_gages2_qf) - len(sigs_gages2_filt)} ({(len(sigs_gages2_qf) - len(sigs_gages2_filt)) / len(sigs_gages2_qf) * 100:.1f}%) GAGES-II gauges did not pass the quality control"
)

# %% (3) Filter out overland flow signatures where significant snow

row_mask_idx = sigs_gages2_filt["SNOW_PCT_PRECIP"] > frac_snow_thresh * 100
print("row_mask_idx sum:", row_mask_idx.sum())

columns_mask = [
    "R_Pvol_RC",
    "R_Pint_RC",
]

# Apply the mask using the boolean values directly
sigs_gages2_filt.loc[row_mask_idx.values, columns_mask] = np.nan

print(
    "\nAfter masking - number of non-null IE_effect values:",
    (~pd.isna(sigs_gages2_filt.R_Pvol_RC)).sum(),
)
print(
    "After quality controlling the IE/SE signatures by snow, "
    + f"{(~pd.isna(sigs_gages2_filt.R_Pvol_RC)).sum()} gauges survived ({(~pd.isna(sigs_gages2_filt.R_Pvol_RC)).sum() / len(sigs_gages2_filt) * 100:.1f} %)"
)

# %% #####################################################################
# CONCAT BOTH DATASETS
##########################################################################

select_cols = [
    "gauge_num",
    "data_name",
    "R_Pvol_RC",
    "R_Pint_RC",
    "n_events",
]

sigs_out = pd.concat([sigs_caravan_filt, sigs_gages2_filt])
sigs_out = sigs_out[select_cols]
sigs_out["gauge_num"] = sigs_out["gauge_num"].astype(str).str.zfill(8)

# %% Drop where R_Pvol_RC is nan
sigs_out = sigs_out[~sigs_out["R_Pvol_RC"].isna()]
sigs_out = sigs_out[~sigs_out["R_Pint_RC"].isna()]

# %% Drop duplicating gauge_num. Prioritize dataset_name camels > hysets > gages2 if overlap
priority_order = {"camels": 0, "hysets": 1, "gages2": 2}
sigs_out_dup = sigs_out.copy()
sigs_out["order"] = sigs_out["data_name"].map(priority_order)
sigs_out = sigs_out.sort_values(
    ["gauge_num", "order"], ascending=[True, True]
).drop_duplicates(subset=["gauge_num"], keep="first")
print(
    f"After dropping duplicating gauge_num, {len(sigs_out)} gauges (left) out of {len(sigs_out_dup)} (original) ({len(sigs_out) / len(sigs_out_dup) * 100:.1f}%)"
)

# %%
sigs_out.to_csv(os.path.join(sig_dir, "out_sigEvent_cara_gg2.csv"), index=False)

# %%
