# %% Post proces signatures calculated for Caravan gages

import pandas as pd
import os
import numpy as np

# %% ____________________________________________________________
# Config

shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
local_dir = r"E:\data"

# Specify signature output directory
sig_outdir = os.path.join(shared_drive, "out", "signatures")
hys_dir = "caravan_hysets_20260716"  # 20250525 is the HESS version
camels_dir = "caravan_camels_20260716"  # 20250525 is the HESS version
caravan_dir = "caravan_us_20260716"  # 20250525 is the HESS version
results_filename = "out_calc_All_custom_shortlist"
results_file = f"{results_filename}.csv"

out_dir = os.path.join(sig_outdir, caravan_dir)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Caravan attributes directory
attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
hys_qa_file = os.path.join(
    shared_drive, "out", "caravan_datacheck", "hysets_summary.csv"
)
attrs_gages2_file = os.path.join(
    shared_drive, "data", "GAGES2", "GAGES_II_attrs", "gagesII_sept30_2011_concat.csv"
)

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

# %% ____________________________________________________________
# Load signatures

# Hysets signatures
_sigs_hys = pd.read_csv(os.path.join(sig_outdir, hys_dir, results_file))
_attrs_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_other_hysets.csv")
)
attrs_hys = _attrs_hys.loc[_attrs_hys["country"] == "United States of America"]
print(f"Hysets attributes has {len(attrs_hys)} rows vs signatures {len(_sigs_hys)}")

sigs_hys = _sigs_hys.merge(attrs_hys, on="gauge_id", how="left")
print(
    f"Hysets signature result has {len(sigs_hys)} rows, {len(sigs_hys.columns)} columns"
)

# Get quality control statistics of Hysets
qa_hys = pd.read_csv(hys_qa_file)

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
sigs_hys_qf = sigs_hys.merge(qa_hys, on="gauge_id")
sigs_hys_filt = sigs_hys[sigs_hys_qf["qf_overall"]]

print(f"{len(sigs_hys_filt)} Hysets watershed left after Quality Assessment")

# %%
# Camels (CAMELS data have good data quality in general, so apply no filtering)
_sigs_camels = pd.read_csv(os.path.join(sig_outdir, camels_dir, results_file))
attrs_camels = pd.read_csv(
    os.path.join(attrs_dir, "camels", "attributes_other_camels.csv")
)
sigs_camels = _sigs_camels.merge(attrs_camels, on="gauge_id")
print(
    f"Camels signature result has {len(sigs_camels)} rows, {len(sigs_camels.columns)} columns"
)

# %% ____________________________________________________________
# (2) Filter out the Hysets gauge_id that are overlapping with CAMELS

# get the USGS gauge number from gauge ID
# get gauge_num in each df by getting the second element of gauge_id, deliminating it with _ (underscore)
sigs_hys_filt["gauge_num"] = sigs_hys_filt["gauge_id"].apply(lambda x: x.split("_")[1])
sigs_camels["gauge_num"] = sigs_camels["gauge_id"].apply(lambda x: x.split("_")[1])

# Check which gauge_num overlap
overlapping_gauges = set(sigs_camels["gauge_num"]).intersection(
    set(sigs_hys_filt["gauge_num"])
)
print(f"There are {len(overlapping_gauges)} overlapping CAMELS and HYSETS gages")
print(overlapping_gauges)


# Check where gauge_lat and gauge_lon overlaps (if it's the same set as above)
overlapping_gauges_latlon = sigs_camels[
    ~sigs_camels["gauge_num"].isin(overlapping_gauges)
    & sigs_camels[["gauge_lat", "gauge_lon"]]
    .apply(tuple, axis=1)
    .isin(sigs_hys_filt[["gauge_lat", "gauge_lon"]].apply(tuple, axis=1))
]["gauge_num"].tolist()
print(overlapping_gauges_latlon)  # This should return nothing
print(len(overlapping_gauges_latlon))  # This should return zero

# %% ____________________________________________________________
# Join camels + hysets. Prioritize camels if hysets gauge overlaps

sigs = (
    sigs_camels.set_index("gauge_num")
    .combine_first(sigs_hys_filt.set_index("gauge_num"))
    .reset_index()
)
sigs.set_index("gauge_id", inplace=True)
sigs.head()

print(
    f"{len(sigs)} survived, after combining CAMELS {len(sigs_camels)} + HYSETS {len(sigs_hys_filt)} - OVERLAP {len(overlapping_gauges)}"
)
print(
    f", which should be equal to {len(sigs_camels) + len(sigs_hys_filt) - len(overlapping_gauges)}"
)

# ___________________________________________________________
# Save
sigs.to_csv(os.path.join(out_dir, f"{results_filename}_filt_qc.csv"))

# %% ____________________________________________________________
# (3) Mask overland flow signature calculated for snowy area, use "frac_snow_thresh"
# TODO: This is temporary solution. Consider snow or temprature when calculating signature calculation for more regirous analysis

attrs_caravan_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_caravan_hysets.csv"),
    index_col="gauge_id",
)
attrs_caravan_camels = pd.read_csv(
    os.path.join(attrs_dir, "camels", "attributes_caravan_camels.csv"),
    index_col="gauge_id",
)
attrs_caravan = pd.concat([attrs_caravan_hys, attrs_caravan_camels])

sigs_fs = sigs.join(attrs_caravan.frac_snow, how="left")

row_mask_idx = sigs_fs["frac_snow"] > frac_snow_thresh
columns_mask = [
    "IE_thresh_signif",
    "SE_thresh_signif",
    "IE_thresh",
    "SE_thresh",
]

# Filter for all signatures
# columns_mask = [
#     "IE_thresh",
#     "IE_effect",
#     "SE_effect",
#     "IE_thresh_signif",
#     "SE_thresh_signif",
#     "IE_thresh",
#     "SE_thresh",
#     "SE_slope",
#     "Storage_thresh_signif",
#     "Storage_thresh",
#     "R_Pvol_RC",
#     "R_Pint_RC",
# ]

sigs.loc[row_mask_idx, columns_mask] = np.nan

print(
    "After quality controlling the IE/SE signatures by snow, "
    + f"{(~pd.isna(sigs.IE_thresh)).sum()} gauges survived ({(~pd.isna(sigs.IE_thresh)).sum() / len(sigs) * 100:.1f} %)"
)
# Save
sigs.to_csv(os.path.join(out_dir, f"{results_filename}_filt_qc_snow.csv"))

# %%
sigs

# %% (4) Join GAGES2 attributes to check the area error. Drop the rows with area error > 25%
# attrs_gages2_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs.csv"
attrs_gages2 = pd.read_csv(attrs_gages2_file)
# Make sure both columns are string
attrs_gages2["usgs_gauge_id"] = attrs_gages2["usgs_gauge_id"].astype(str).str.zfill(8)
sigs["gauge_num"] = sigs["gauge_num"].astype(str).str.zfill(8)
sigs["gauge_id"] = sigs.index
sigs_gages2 = sigs.merge(
    attrs_gages2, how="left", left_on="gauge_num", right_on="usgs_gauge_id"
)
print(
    f"There are {len(sigs_gages2)} gages in the GAGES2 dataset -- should be same as {len(sigs)}"
)
sigs_gages2.set_index("gauge_id", inplace=True)
sigs_gages2.head()
# %%
sigs_gages2["area_err"] = abs(
    (sigs_gages2["area"] - sigs_gages2["DRAIN_SQKM"]) / sigs_gages2["DRAIN_SQKM"]
)
area_err_idx = sigs_gages2[sigs_gages2["area_err"] > area_err_thresh].index

sigs_qa_area = sigs.drop(index=area_err_idx)

print(f"Area error threshold : (Caravan - GAGES2)/GAGES2 error > {area_err_thresh}")
print(
    f"{len(sigs_qa_area)} survived after area error filtering ({len(sigs_qa_area) / len(sigs) * 100:.1f} %)"
)
print(
    f"{len(area_err_idx)} gages were dropped due to area error ({len(area_err_idx) / len(sigs) * 100:.1f} %)"
)

# Save the updated sigs dataframe
sigs_qa_area.to_csv(os.path.join(out_dir, f"{results_filename}_filt_qc_snow_area.csv"))

# %% ###################################################################
# GET THE SUBSET OF SIGNATURES
########################################################################

# # Skip the gauges with BFI = NaN
# # NOTE: no need to worry about this anymore, no lacking signatures after running the signature calculation on local drive
# bfi_nan_count = sigs_qa_area["BFI"].isna().sum()
# sigs_qa_area = sigs_qa_area[~sigs_qa_area["BFI"].isna()]
# print(
#     f"After dropping the gauges with BFI = NaN ({bfi_nan_count}, {bfi_nan_count / len(sigs_qa_area) * 100:.1f} %): {len(sigs_qa_area)}"
# )
# %% Get the CAMELS subset
sigs_qced_camels_subset = sigs_qa_area[sigs_qa_area.index.str.contains("camels")]
print(f"Caravan signatures after QC, CAMELS subset: {len(sigs_qced_camels_subset)}")
sigs_qced_camels_subset.to_csv(
    os.path.join(out_dir, f"{results_filename}_filt_qc_snow_area_subset_camels.csv")
)

# %% Get the GAGES2 subset
not_in_gages2_idx = sigs_gages2["DRAIN_SQKM"].isna()
sigs_gages2_subset = sigs_qa_area[~not_in_gages2_idx].copy()
print(f"Caravan signatures after QC, GAGES2 subset: {len(sigs_gages2_subset)}")
sigs_gages2_subset.to_csv(
    os.path.join(out_dir, f"{results_filename}_filt_qc_snow_area_subset_gages2.csv")
)

# %%
ref_gage_idx = sigs_gages2["CLASS"] == "Ref"
ref_gages = sigs_gages2[ref_gage_idx]
print(len(ref_gages))
common_gages = list(set(ref_gages.index) & set(sigs_gages2_subset.index))
sigs_gages2_ref_subset = sigs_gages2_subset.loc[common_gages].copy()
print(f"Caravan signatures after QC, GAGES2 subset, Ref: {len(sigs_gages2_ref_subset)}")
sigs_gages2_ref_subset.to_csv(
    os.path.join(out_dir, f"{results_filename}_filt_qc_snow_area_subset_gages2_ref.csv")
)

# %%
