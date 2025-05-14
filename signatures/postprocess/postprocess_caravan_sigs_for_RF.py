# %% Post proces signatures calculated for Caravan gages

import pandas as pd
import os
import numpy as np

# %% ____________________________________________________________
# Config

shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"

sig_outdir = os.path.join(shared_drive, "out", "signatures")

hys_dir = "caravan_hysets_20250223_withWu"
camels_dir = "caravan_camels_20250223_withWu"
caravan_dir = "caravan_us_20250223_withWu"  # "caravan_us_20240609_tunedparams" "gages2_caravan_us_20250211"

out_dir = os.path.join(sig_outdir, caravan_dir)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

results_filename = "out_calc_All_custom"
results_file = f"{results_filename}.csv"

attrs_dir = os.path.join(shared_drive, "data", "Caravan1.4", "attributes")
derived_attrs_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs"
)

hys_qa_file = os.path.join(
    shared_drive, "out", "caravan_datacheck", "hysets_summary.csv"
)

attrs_gages2_file = os.path.join(
    derived_attrs_dir, "assembled_RA", "attrs_gages2_epa.csv"
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

# Hysets
_sigs_hys = pd.read_csv(os.path.join(sig_outdir, hys_dir, results_file))
attrs_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_other_hysets.csv")
)
sigs_hys = _sigs_hys.merge(attrs_hys, on="gauge_id")
print(
    f"Hysets signature result has {len(sigs_hys)} rows, {len(sigs_hys.columns)} columns"
)

# Get quality control statistics of Hysets
qa_hys = pd.read_csv(hys_qa_file)

# ____________________________________________________________
# Quality control of Hysets Signautres

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
# Filter out the Hysets gauge_id that are overlapping with CAMELS

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
# Mask overland flow signature calculated for snowy area, use "frac_snow_thresh"
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

# Alternatively, just load the sigs and mask
# sigs = pd.read_csv(
#     os.path.join(sig_outdir, caravan_dir, "out_calc_All_custom_caravanoverlap.csv"),
#     index_col="gauge_id",
# )

sigs_fs = sigs.join(attrs_caravan.frac_snow, how="left")
row_mask_idx = sigs_fs["frac_snow"] > frac_snow_thresh
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

sigs.loc[row_mask_idx, columns_mask] = np.nan
# %%
print(
    f"{(~pd.isna(sigs.IE_effect)).sum()} survived ({(~pd.isna(sigs.IE_effect)).sum() / len(sigs) * 100:.1f} %)"
)
# %%  ____________________________________________________________
# Save
sigs.to_csv(os.path.join(out_dir, f"{results_filename}_filt_qc_snow.csv"))

# %%
attrs_gages2 = pd.read_csv(attrs_gages2_file, index_col="gauge_id").drop(
    columns=["gauge_name", "country", "gauge_lat", "gauge_lon", "area"]
)
sigs_gages2 = sigs.join(attrs_gages2, how="left")
sigs_gages2["area_err"] = abs(
    (sigs_gages2["area"] - sigs_gages2["DRAIN_SQKM"]) / sigs_gages2["DRAIN_SQKM"]
)
area_err_idx = sigs_gages2[sigs_gages2["area_err"] > 0.25].index
print(area_err_idx)
# %%
# Drop the rows with the area_err_idx from sigs dataframe
sigs_qa_area = sigs.drop(index=area_err_idx)

print(
    f"{len(sigs_qa_area)} survived after area error filtering ({len(sigs_qa_area) / len(sigs) * 100:.1f} %)"
)
print(
    f"{len(area_err_idx)} gages were dropped due to area error ({len(area_err_idx) / len(sigs) * 100:.1f} %)"
)

# %%

# Save the updated sigs dataframe
sigs_qa_area.to_csv(os.path.join(out_dir, f"{results_filename}_filt_qc_snow_area.csv"))

# %%
