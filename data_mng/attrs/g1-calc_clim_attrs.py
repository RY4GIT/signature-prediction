# %% import os
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import List

import matplotlib.pyplot as plt
# %%


def _split_list(a_list: List) -> List:
    """Splits list into list of lists, where each list contains subsequent numbers.
    This code has been taken and modified from the Caravan project/dataset.
    See https://github.com/kratzert/Caravan for details."""
    new_list = []
    start = 0
    for index, value in enumerate(a_list):
        if index < len(a_list) - 1:
            if a_list[index + 1] > value + 1:
                end = index + 1
                new_list.append(a_list[start:end])
                start = end
        else:
            new_list.append(a_list[start : len(a_list)])
    return new_list


def _get_precip_stats(precip_series):
    """Calculate precipitation statistics for a single gauge.
    This code has been taken and modified from the Caravan project/dataset.
    See https://github.com/kratzert/Caravan for details."""

    p_mean = precip_series.mean()

    # Calculate frequencies
    high_prec_freq = len(precip_series[precip_series >= 5 * p_mean]) / len(
        precip_series
    )
    low_prec_freq = len(precip_series[precip_series < 1]) / len(precip_series)

    # Calculate durations
    precip = precip_series.values
    idx = np.where(precip < 1)[0]
    groups = _split_list(idx)
    if groups:
        low_precip_dur = np.mean(np.array([len(p) for p in groups]))
    else:
        low_precip_dur = 0.0

    idx = np.where(precip >= 5 * p_mean)[0]
    groups = _split_list(idx)
    if groups:
        high_prec_dur = np.mean(np.array([len(p) for p in groups]))
    else:
        high_prec_dur = 0.0

    return {
        "high_prec_freq": high_prec_freq,
        "low_prec_freq": low_prec_freq,
        "low_precip_dur": low_precip_dur,
        "high_prec_dur": high_prec_dur,
    }


def _get_moisture_and_seasonality_index(precipitation, pet) -> tuple[float, float]:
    """Calculate annual moisture index and seasonality index for a single gauge.
    This code has been taken and modified from the Caravan project/dataset.
    See https://github.com/kratzert/Caravan for details."""
    mean_monthly_precip = precipitation.groupby(precipitation.index.month).mean()
    mean_monthly_pet = pet.groupby(pet.index.month).mean()

    # Average annual moisture index (see Knoben)
    p_gt_et = (
        1
        - mean_monthly_pet.loc[mean_monthly_precip > mean_monthly_pet]
        / mean_monthly_precip.loc[mean_monthly_precip > mean_monthly_pet]
    )
    srs = pd.Series(
        np.zeros((12), dtype=np.float32), index=mean_monthly_pet.index, name="dummy"
    )
    p_eq_et = srs.loc[mean_monthly_precip == mean_monthly_pet]
    p_lt_et = (
        mean_monthly_precip.loc[mean_monthly_precip < mean_monthly_pet]
        / mean_monthly_pet.loc[mean_monthly_precip < mean_monthly_pet]
        - 1
    )
    monthly_moisture_index = pd.concat([p_gt_et, p_eq_et, p_lt_et])

    annual_moisture_index = monthly_moisture_index.mean()

    # Seasonality (see Knoben)
    seasonality = monthly_moisture_index.max() - monthly_moisture_index.min()

    return annual_moisture_index, seasonality


# %% ############################################################
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
gridmet_dir = os.path.join(data_dir, "GAGES2_gridMET")

precip_file = os.path.join(gridmet_dir, "pr_mm_gridmet_conus_gaged_1980_2020_mean.csv")
pet_file = os.path.join(gridmet_dir, "pet_mm_gridmet_conus_gaged_1980_2020_mean.csv")
##################################################################

# %%####################
# LOAD DATA
########################
precip = pd.read_csv(precip_file)
pet = pd.read_csv(pet_file)

# %%####################
# PREPARE DATA
########################
precip["Date"] = pd.to_datetime(precip["Date"], format="%Y-%m-%d")
precip.set_index("Date", inplace=True)

pet["Date"] = pd.to_datetime(pet["Date"], format="%Y-%m-%d")
pet.set_index("Date", inplace=True)


# %%####################
# CALCULATE CLIMATE ATTRIBUTES: SIMPLE
########################
p_mean_gridmet = precip.mean(axis=0)
pet_mean_gridmet = pet.mean(axis=0)
aridity_gridmet = pet_mean_gridmet / p_mean_gridmet

# %%####################
# CALCULATE CLIMATE ATTRIBUTES: BY GAUGE
########################

# Initialize empty DataFrames to store results
annual_moisture_index_gridmet = pd.Series(index=precip.columns)
seasonality_gridmet = pd.Series(index=precip.columns)
precip_stats = pd.DataFrame(
    index=precip.columns,
    columns=[
        "high_prec_freq",
        "low_prec_freq",
        "low_precip_dur",
        "high_prec_dur",
    ],
)

# Get common gauge IDs
common_gauges = precip.columns.intersection(pet.columns)

# Iterate through each gauge
for gauge_id in tqdm(common_gauges):
    # Get the precipitation and PET series for this gauge
    precip_series = precip[gauge_id]
    pet_series = pet[gauge_id]

    # Calculate moisture index and seasonality for this gauge
    annual_moisture_index_gridmet[gauge_id], seasonality_gridmet[gauge_id] = (
        _get_moisture_and_seasonality_index(
            precipitation=precip_series,
            pet=pet_series,
        )
    )

    # Calculate precipitation statistics
    stats = _get_precip_stats(precip_series)
    for stat_name, value in stats.items():
        precip_stats.loc[gauge_id, stat_name] = value


# %%####################
# CONCATENATE CLIMATE ATTRIBUTES
########################
clim_attrs = pd.concat(
    [
        p_mean_gridmet.rename("p_mean_mm_gridmet"),
        pet_mean_gridmet.rename("pet_mean_mm_gridmet"),
        aridity_gridmet.rename("aridity_gridmet"),
        annual_moisture_index_gridmet.rename("annual_moisture_index_gridmet"),
        seasonality_gridmet.rename("seasonality_gridmet"),
        precip_stats.rename(
            columns={
                "high_prec_freq": "high_prec_freq_gridmet",
                "low_prec_freq": "low_prec_freq_gridmet",
                "low_precip_dur": "low_precip_dur_gridmet",
                "high_prec_dur": "high_prec_dur_gridmet",
            },
        ),
    ],
    axis=1,
)

clim_attrs.index.name = "usgs_gauge_id"
clim_attrs.head()
# %%####################
# SAVE CLIMATE ATTRIBUTES
########################
clim_attrs.to_csv(os.path.join(gridmet_dir, "clim_attrs_gridmet.csv"))


# %%
clim_attrs.head()
# %%####################################################################################################
# COMPARE CLIMATE ATTRIBUTES
########################################################################################################
cara_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv"
cara_attrs = pd.read_csv(cara_attrs_file)
cara_attrs["usgs_gauge_id"] = (
    cara_attrs["gauge_id"].astype(str).str.split("_").str[1].str.zfill(8)
)

# %%
attrs_merged = pd.merge(cara_attrs, clim_attrs, on="usgs_gauge_id", how="inner")

# %%
attrs_merged
# %% ######################################################
# Check some Caravan-GAGES2 equivalent attributes
# ######################################################

# Create a list of all attribute pairs to plot
attr_pairs = [
    ("p_mean", "p_mean_mm_gridmet", "Precipitation"),
    ("pet_mean_FAO_PM", "pet_mean_mm_gridmet", "PET"),
    ("aridity_FAO_PM", "aridity_gridmet", "Aridity"),
    ("moisture_index_FAO_PM", "annual_moisture_index_gridmet", "Moisture index"),
    ("seasonality_FAO_PM", "seasonality_gridmet", "Seasonality (*)"),
    ("high_prec_freq", "high_prec_freq_gridmet", "High precip frequency (*)"),
    ("low_prec_freq", "low_prec_freq_gridmet", "Low precip frequency (*)"),
    ("low_prec_dur", "low_precip_dur_gridmet", "Low precip duration (*)"),
    ("high_prec_dur", "high_prec_dur_gridmet", "High precip duration"),
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
    cara_var = attrs_merged[cara_varname].astype(float)
    gages2_var = attrs_merged[gages2_varname].astype(float)

    axs[i].scatter(cara_var, gages2_var, s=1, alpha=0.5)

    try:
        nan_mask = ~np.isnan(cara_var) & ~np.isnan(gages2_var)
        pearson_corr = np.corrcoef(cara_var[nan_mask], gages2_var[nan_mask])[0, 1]
    except Exception as e:
        print(e)
        pearson_corr = np.nan

    # Add 1:1 line
    lims = [
        min(min(cara_var), min(gages2_var)) * 1.1,
        max(max(cara_var), max(gages2_var)) * 1.1,
    ]
    axs[i].plot(lims, lims, "k--", alpha=0.5, zorder=0)

    axs[i].set_title(title)
    axs[i].set_xlabel(f"{cara_varname}")
    axs[i].set_ylabel(f"{gages2_varname}")
    axs[i].set_xlim(lims)
    axs[i].set_ylim(lims)
    # Show median values and correlation
    axs[i].text(
        0.05,
        0.95,
        f"ERA5-FAO-PM: {cara_var.median():.2f}\ngridMET: {gages2_var.median():.2f}\npearson r: {pearson_corr:.2f}",
        transform=axs[i].transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )

# Remove empty subplots if any
for i in range(len(attr_pairs), len(axs)):
    fig.delaxes(axs[i])

plt.tight_layout()
fig.savefig(os.path.join(gridmet_dir, "climate_attrs_comparison.png"))
