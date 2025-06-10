# %%
import os
import pandas as pd
import numpy as np

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"
gridmet_sigs_dir = "gages2_20250608"
caravan_sigs_dir = "caravan_us_20250525"
out_dir = os.path.join(sig_dir, gridmet_sigs_dir)


gridmet_sigs_file = os.path.join(sig_dir, gridmet_sigs_dir, "out_calc_All_custom.csv")
caravan_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_caravan_us_epa.csv"

# %%
gridmet_sigs = pd.read_csv(gridmet_sigs_file)
gridmet_sigs["gauge_id"] = gridmet_sigs["gauge_id"].astype(str).str.zfill(8)
# %%
caravan_attrs = pd.read_csv(caravan_attrs_file)
caravan_attrs["usgs_gauge_id"] = (
    caravan_attrs["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)
# %%
attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
gages2_attrs = pd.read_csv(attrs_file)
gages2_attrs["gauge_id"] = gages2_attrs["STAID"].astype(str).str.zfill(8)

# %%
qa_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\caravan_datacheck\gages2_summary.csv"
qa_gages2 = pd.read_csv(qa_file)
qa_gages2["gauge_id"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)


# %% (1) Get GAGES-II gauges that are not overlapping with caravan
gridmet_sigs_not_in_caravan = gridmet_sigs[
    ~gridmet_sigs["gauge_id"].isin(caravan_attrs["usgs_gauge_id"])
]
gages2_attrs_not_in_caravan = gages2_attrs[
    ~gages2_attrs["gauge_id"].isin(caravan_attrs["usgs_gauge_id"])
]
print("Original number of GAGES-II gauges: \n", len(gages2_attrs))
print(
    f"GAGES-II gauges not overlapping with caravan:\n {len(gridmet_sigs_not_in_caravan)} ({len(gages2_attrs_not_in_caravan) / len(gages2_attrs) * 100:.2f}%)"
)

# %% (1.2) Filter by lat lon (limit to US)
# Get the bounding box of the US
us_bbox = (
    -124.848974,
    24.396308,
    -66.885444,
    49.384358,
)
gages2_attrs["gauge_id"] = gages2_attrs["gauge_id"].astype(str).str.zfill(8)
gridmet_sigs_not_in_caravan["gauge_id"] = (
    gridmet_sigs_not_in_caravan["gauge_id"].astype(str).str.zfill(8)
)
print(len(gridmet_sigs_not_in_caravan))
gridmet_sigs = gridmet_sigs_not_in_caravan.merge(gages2_attrs, on="gauge_id")
print(len(gridmet_sigs))

# %% Filter by lat and long
mask = (
    (gridmet_sigs["LAT_GAGE"] > us_bbox[1])
    & (gridmet_sigs["LAT_GAGE"] < us_bbox[3])
    & (gridmet_sigs["LNG_GAGE"] > us_bbox[0])
    & (gridmet_sigs["LNG_GAGE"] < us_bbox[2])
)
print(len(gridmet_sigs))
gridmet_sigs = gridmet_sigs[mask]
print(len(gridmet_sigs))


# %%

# %% (2) Get GAGES-II gauges with good data quality based on QA results

##################################################################
# QUALITY CONTROL THRESHOLDS

# Filter signatures by duration of the record
duration_thresh = 5  # in years

# Filer by the nan fraction in the available (non-NaN) data record
subset_nan_fraction_thresh = 0.3  # in fraction (-)

# Mask overland flow signature calculated for snowy area
perc_snow_thresh = 20  # in percent

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
gridmet_sigs["gauge_id"] = gridmet_sigs["gauge_id"].astype(str).str.zfill(8)
qa_gages2["gauge_id"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)
sigs_gages2_qf = gridmet_sigs.merge(qa_gages2, on="gauge_id")
sigs_gages2_filt = sigs_gages2_qf[sigs_gages2_qf["qf_overall"]].copy()

print(
    f"Original number of GAGES-II gauges not in Caravan: \n {len(gages2_attrs_not_in_caravan)}"
)
print(
    f"{len(sigs_gages2_filt)} GAGES-II gauges left after Quality Assessment ({len(sigs_gages2_filt) / len(gages2_attrs_not_in_caravan) * 100:.1f}%)"
)
print(
    f"{len(sigs_gages2_qf) - len(sigs_gages2_filt)} ({(len(sigs_gages2_qf) - len(sigs_gages2_filt)) / len(sigs_gages2_qf) * 100:.1f}%) GAGES-II gauges did not pass the quality control"
)


# %%

# %% (3) Filter out overland flow signatures where significant snow
print(len(sigs_gages2_filt))
df = sigs_gages2_filt.copy()
print(len(df))


row_mask_idx = df["SNOW_PCT_PRECIP"] > perc_snow_thresh
print("row_mask_idx sum:", row_mask_idx.sum())

columns_mask = [
    "IE_thresh",
    "IE_effect",
    "SE_effect",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "IE_thresh",
    "SE_thresh",
    "SE_slope",
    "Storage_thresh_signif",
    "Storage_thresh",
    "R_Pvol_RC",
    "R_Pint_RC",
]

# # Check which columns exist in the dataframe
# print("\nChecking columns:")
# for col in columns_mask:
#     if col in df.columns:
#         print(f"{col} exists, non-null count before masking: {df[col].count()}")
#     else:
#         print(f"{col} does NOT exist in dataframe")


# Apply the mask using the boolean values directly
df.loc[row_mask_idx.values, columns_mask] = np.nan

print(
    "\nAfter masking - number of non-null IE_effect values:",
    (~pd.isna(df.IE_effect)).sum(),
)
print(
    "After quality controlling the IE/SE signatures by snow, "
    + f"{(~pd.isna(df.IE_effect)).sum()} gauges survived ({(~pd.isna(df.IE_effect)).sum() / len(df) * 100:.1f} %)"
)


# Save
df.to_csv(os.path.join(out_dir, f"out_calc_All_custom_filt_qc_snow.csv"), index=False)

# %%
