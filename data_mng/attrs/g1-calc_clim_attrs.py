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


def _get_frac_snow(precipitation, temperature):
    # Fraction of mean monthly precipipitation falling as snow (see Knoben)
    mean_monthly_precip = precipitation.groupby(precipitation.index.month).mean()
    mean_monthly_temp = temperature.groupby(temperature.index.month).mean()
    frac_snow = (
        mean_monthly_precip.loc[mean_monthly_temp < 0].sum() / mean_monthly_precip.sum()
    )
    return frac_snow


# %% ############################################################
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
gridmet_dir = r"D:\data\GAGES2_gridMET"
cloud_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2_gridMET"
)
precip_file = os.path.join(gridmet_dir, "pr_mm_gridmet_conus_gaged_1980_2020_mean.csv")
pet_file = os.path.join(gridmet_dir, "pet_mm_gridmet_conus_gaged_1980_2020_mean.csv")
temp_max_file = os.path.join(
    gridmet_dir, "tmmx_degc_gridmet_conus_gaged_1980_2020_mean.csv"
)
temp_min_file = os.path.join(
    gridmet_dir, "tmmn_degc_gridmet_conus_gaged_1980_2020_mean.csv"
)
##################################################################

# %%####################
# LOAD DATA
########################
print("Loading precipitation data")
precip = pd.read_csv(precip_file)
print("Loading PET data")
pet = pd.read_csv(pet_file)
print("Loading temperature data : max")
temp_max = pd.read_csv(temp_max_file)
print("Loading temperature data : min")
temp_min = pd.read_csv(temp_min_file)

# %%####################
# PREPARE DATA
########################
precip["Date"] = pd.to_datetime(precip["Date"], format="%Y-%m-%d")
precip.set_index("Date", inplace=True)

pet["Date"] = pd.to_datetime(pet["Date"], format="%Y-%m-%d")
pet.set_index("Date", inplace=True)

temp_max["Date"] = pd.to_datetime(temp_max["Date"], format="%Y-%m-%d")
temp_max.set_index("Date", inplace=True)

temp_min["Date"] = pd.to_datetime(temp_min["Date"], format="%Y-%m-%d")
temp_min.set_index("Date", inplace=True)

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
frac_snow_gridmet = pd.Series(index=precip.columns)
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
    temp_max_series = temp_max[gauge_id]
    temp_min_series = temp_min[gauge_id]
    temp_series = (temp_max_series + temp_min_series) / 2

    # Calculate moisture index and seasonality for this gauge
    annual_moisture_index_gridmet[gauge_id], seasonality_gridmet[gauge_id] = (
        _get_moisture_and_seasonality_index(
            precipitation=precip_series,
            pet=pet_series,
        )
    )
    frac_snow_gridmet[gauge_id] = _get_frac_snow(
        precipitation=precip_series,
        temperature=temp_series,
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
        frac_snow_gridmet.rename("frac_snow_gridmet"),
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
clim_attrs.to_csv(os.path.join(cloud_dir, "clim_attrs_gridmet.csv"))


# %%####################################################################################################
# COMPARE CLIMATE ATTRIBUTES
########################################################################################################

# %%
clim_attrs = pd.read_csv(os.path.join(gridmet_dir, "clim_attrs_gridmet.csv"))
clim_attrs["usgs_gauge_id"] = clim_attrs["usgs_gauge_id"].astype(str).str.zfill(8)
clim_attrs.set_index("usgs_gauge_id", inplace=True)
clim_attrs.head()

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
    ("frac_snow", "frac_snow_gridmet", "Fraction of snow (*)"),
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
fig.savefig(os.path.join(cloud_dir, "climate_attrs_comparison.png"))

# %% ######################################################
# Get linear regression to relate ERA-5-FAO-PM and gridMET climate attributes (PET and Aridity  )
# ######################################################

from scipy import stats
import matplotlib.pyplot as plt

# Define the attribute pairs for regression analysis
regression_pairs = [
    ("pet_mean_FAO_PM", "pet_mean_mm_gridmet", "PET (mm/day)"),
    ("aridity_FAO_PM", "aridity_gridmet", "Aridity (PET/P)"),
]

# Create figure for regression plots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Store regression results
regression_results = {}

for i, (x_var, y_var, title) in enumerate(regression_pairs):
    # Get data and remove NaN values
    x_data = attrs_merged[x_var].astype(float)
    y_data = attrs_merged[y_var].astype(float)

    # Create mask for valid data points
    valid_mask = ~np.isnan(x_data) & ~np.isnan(y_data)
    x_clean = x_data[valid_mask]
    y_clean = y_data[valid_mask]

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    r_squared = r_value**2

    # Store results
    regression_results[title] = {
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "r_squared": r_squared,
        "p_value": p_value,
        "std_err": std_err,
        "n_points": len(x_clean),
    }

    # Create scatter plot
    axes[i].scatter(x_clean, y_clean, alpha=0.6, s=10)

    # Plot regression line
    x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
    y_pred = slope * x_range + intercept
    axes[i].plot(
        x_range, y_pred, "r-", linewidth=2, label=f"y = {slope:.3f}x + {intercept:.3f}"
    )

    # Add 1:1 line for reference
    lims = [min(x_clean.min(), y_clean.min()), max(x_clean.max(), y_clean.max())]
    axes[i].plot(lims, lims, "k--", alpha=0.5, linewidth=1, label="1:1 line")

    # Set labels and title
    axes[i].set_xlabel(f"ERA5-FAO-PM {title}")
    axes[i].set_ylabel(f"gridMET {title}")
    axes[i].set_title(f"{title} Regression Analysis")

    # Add statistics text
    stats_text = (
        f"R² = {r_squared:.3f}\n"
        f"slope = {slope:.3f}\n"
        f"intercept = {intercept:.3f}\n"
        f"p-value = {p_value:.2e}\n"
        f"n = {len(x_clean)}"
    )

    axes[i].text(
        0.05,
        0.95,
        stats_text,
        transform=axes[i].transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    axes[i].legend()
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig(
    os.path.join(gridmet_dir, "climate_attrs_regression_analysis.png"),
    dpi=300,
    bbox_inches="tight",
)
fig.savefig(
    os.path.join(cloud_dir, "climate_attrs_regression_analysis.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.show()

# Print detailed regression results
print("\n" + "=" * 80)
print("LINEAR REGRESSION RESULTS: ERA5-FAO-PM vs gridMET Climate Attributes")
print("=" * 80)

for attr_name, results in regression_results.items():
    print(f"\n{attr_name}:")
    print(
        f"  Regression equation: y = {results['slope']:.4f}x + {results['intercept']:.4f}"
    )
    print(f"  Correlation coefficient (r): {results['r_value']:.4f}")
    print(f"  Coefficient of determination (R²): {results['r_squared']:.4f}")
    print(f"  P-value: {results['p_value']:.2e}")
    print(f"  Standard error: {results['std_err']:.4f}")
    print(f"  Sample size: {results['n_points']}")

    # Interpretation
    if results["r_squared"] > 0.8:
        strength = "very strong"
    elif results["r_squared"] > 0.6:
        strength = "strong"
    elif results["r_squared"] > 0.4:
        strength = "moderate"
    elif results["r_squared"] > 0.2:
        strength = "weak"
    else:
        strength = "very weak"

    significance = "significant" if results["p_value"] < 0.05 else "not significant"

    print(f"  Interpretation: {strength} correlation, {significance} at α=0.05")

print("\n" + "=" * 80)

# %%

# %% ######################################################
# APPLY BIAS CORRECTION TO GRIDMET CLIMATE ATTRIBUTES
# ######################################################

print("Applying bias correction to gridMET climate attributes...")

# Apply bias correction using the regression results
# For PET: pet_gridmet_biascorr = (pet_gridmet - intercept) / slope
# For Aridity: aridity_gridmet_biascorr = (aridity_gridmet - intercept) / slope

# Get regression parameters
pet_slope = regression_results["PET (mm/day)"]["slope"]
pet_intercept = regression_results["PET (mm/day)"]["intercept"]
aridity_slope = regression_results["Aridity (PET/P)"]["slope"]
aridity_intercept = regression_results["Aridity (PET/P)"]["intercept"]

print(f"PET regression: y = {pet_slope:.4f}x + {pet_intercept:.4f}")
print(f"Aridity regression: y = {aridity_slope:.4f}x + {aridity_intercept:.4f}")

# Apply inverse regression to bias-correct gridMET values
# Inverse: x = (y - intercept) / slope
clim_attrs["pet_gridmet_biascorr"] = (
    clim_attrs["pet_mean_mm_gridmet"] - pet_intercept
) / pet_slope
clim_attrs["aridity_gridmet_biascorr"] = (
    clim_attrs["aridity_gridmet"] - aridity_intercept
) / aridity_slope

print("Bias correction applied successfully!")
print(
    f"Original PET range: {clim_attrs['pet_mean_mm_gridmet'].min():.2f} - {clim_attrs['pet_mean_mm_gridmet'].max():.2f}"
)
print(
    f"Bias-corrected PET range: {clim_attrs['pet_gridmet_biascorr'].min():.2f} - {clim_attrs['pet_gridmet_biascorr'].max():.2f}"
)
print(
    f"Original aridity range: {clim_attrs['aridity_gridmet'].min():.2f} - {clim_attrs['aridity_gridmet'].max():.2f}"
)
print(
    f"Bias-corrected aridity range: {clim_attrs['aridity_gridmet_biascorr'].min():.2f} - {clim_attrs['aridity_gridmet_biascorr'].max():.2f}"
)

# Save updated climate attributes with bias correction
clim_attrs.to_csv(os.path.join(gridmet_dir, "clim_attrs_gridmet_biascorr.csv"))
clim_attrs.to_csv(os.path.join(cloud_dir, "clim_attrs_gridmet_biascorr.csv"))
print("Updated climate attributes saved with bias correction!")

# Display summary of the updated dataframe
print(f"\nUpdated clim_attrs shape: {clim_attrs.shape}")
print("New columns added: pet_gridmet_biascorr, aridity_gridmet_biascorr")
print("\nFirst few rows of bias-corrected attributes:")
print(
    clim_attrs[
        [
            "pet_mean_mm_gridmet",
            "pet_gridmet_biascorr",
            "aridity_gridmet",
            "aridity_gridmet_biascorr",
        ]
    ].head()
)


# %% ######################################################
# VALIDATE BIAS CORRECTION: PLOT CORRECTED vs ERA5-FAO-PM
# ######################################################

print("Creating validation plots for bias correction...")

# Merge bias-corrected gridMET with ERA5-FAO-PM for validation
validation_data = pd.merge(cara_attrs, clim_attrs, on="usgs_gauge_id", how="inner")

# Create figure for validation plots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Define validation pairs: [original vs reference, corrected vs reference]
validation_pairs = [
    # Original comparisons
    (
        "pet_mean_FAO_PM",
        "pet_mean_mm_gridmet",
        "Original PET: ERA5-FAO-PM vs gridMET",
        axes[0, 0],
    ),
    (
        "aridity_FAO_PM",
        "aridity_gridmet",
        "Original Aridity: ERA5-FAO-PM vs gridMET",
        axes[0, 1],
    ),
    # Bias-corrected comparisons
    (
        "pet_mean_FAO_PM",
        "pet_gridmet_biascorr",
        "Bias-Corrected PET: ERA5-FAO-PM vs gridMET",
        axes[1, 0],
    ),
    (
        "aridity_FAO_PM",
        "aridity_gridmet_biascorr",
        "Bias-Corrected Aridity: ERA5-FAO-PM vs gridMET",
        axes[1, 1],
    ),
]

validation_stats = {}

for ref_var, comp_var, title, ax in validation_pairs:
    # Get data and remove NaN values
    ref_data = validation_data[ref_var].astype(float)
    comp_data = validation_data[comp_var].astype(float)

    # Create mask for valid data points
    valid_mask = ~np.isnan(ref_data) & ~np.isnan(comp_data)
    ref_clean = ref_data[valid_mask]
    comp_clean = comp_data[valid_mask]

    # Calculate statistics
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        ref_clean, comp_clean
    )
    r_squared = r_value**2

    # Calculate RMSE and bias
    rmse = np.sqrt(np.mean((comp_clean - ref_clean) ** 2))
    bias = np.mean(comp_clean - ref_clean)

    # Store validation statistics
    validation_stats[title] = {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "rmse": rmse,
        "bias": bias,
        "n_points": len(ref_clean),
    }

    # Create scatter plot
    ax.scatter(ref_clean, comp_clean, alpha=0.6, s=15, color="blue")

    # Plot regression line
    x_range = np.linspace(ref_clean.min(), ref_clean.max(), 100)
    y_pred = slope * x_range + intercept
    ax.plot(
        x_range,
        y_pred,
        "r-",
        linewidth=2,
        label=f"Regression: y = {slope:.3f}x + {intercept:.3f}",
    )

    # Add perfect 1:1 line for reference
    lims = [
        min(ref_clean.min(), comp_clean.min()),
        max(ref_clean.max(), comp_clean.max()),
    ]
    ax.plot(lims, lims, "k--", alpha=0.7, linewidth=2, label="Perfect 1:1 line")

    # Set labels and title
    ax.set_xlabel(f"{ref_var.replace('_', ' ').title()}")
    ax.set_ylabel(f"{comp_var.replace('_', ' ').title()}")
    ax.set_title(title)

    # Add statistics text
    stats_text = (
        f"R² = {r_squared:.3f}\n"
        f"RMSE = {rmse:.3f}\n"
        f"Bias = {bias:.3f}\n"
        f"Slope = {slope:.3f}\n"
        f"n = {len(ref_clean)}"
    )

    ax.text(
        0.05,
        0.95,
        stats_text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
    )

    ax.legend()
    ax.grid(True, alpha=0.3)

    # Set equal aspect ratio for better visual comparison
    ax.set_aspect("equal", adjustable="box")

plt.tight_layout()
fig.savefig(
    os.path.join(gridmet_dir, "bias_correction_validation.png"),
    dpi=300,
    bbox_inches="tight",
)
fig.savefig(
    os.path.join(cloud_dir, "bias_correction_validation.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.show()

# Print validation results
print("\n" + "=" * 80)
print("BIAS CORRECTION VALIDATION RESULTS")
print("=" * 80)

print("\nComparison of original vs bias-corrected performance:")
print("-" * 60)

# Compare original vs corrected performance
original_pet_r2 = validation_stats["Original PET: ERA5-FAO-PM vs gridMET"]["r_squared"]
corrected_pet_r2 = validation_stats["Bias-Corrected PET: ERA5-FAO-PM vs gridMET"][
    "r_squared"
]
original_pet_rmse = validation_stats["Original PET: ERA5-FAO-PM vs gridMET"]["rmse"]
corrected_pet_rmse = validation_stats["Bias-Corrected PET: ERA5-FAO-PM vs gridMET"][
    "rmse"
]
original_pet_bias = validation_stats["Original PET: ERA5-FAO-PM vs gridMET"]["bias"]
corrected_pet_bias = validation_stats["Bias-Corrected PET: ERA5-FAO-PM vs gridMET"][
    "bias"
]

print("PET:")
print(
    f"  R² improvement: {original_pet_r2:.3f} → {corrected_pet_r2:.3f} ({corrected_pet_r2 - original_pet_r2:+.3f})"
)
print(
    f"  RMSE change: {original_pet_rmse:.3f} → {corrected_pet_rmse:.3f} ({corrected_pet_rmse - original_pet_rmse:+.3f})"
)
print(
    f"  Bias reduction: {original_pet_bias:.3f} → {corrected_pet_bias:.3f} ({abs(corrected_pet_bias) - abs(original_pet_bias):+.3f})"
)

original_arid_r2 = validation_stats["Original Aridity: ERA5-FAO-PM vs gridMET"][
    "r_squared"
]
corrected_arid_r2 = validation_stats["Bias-Corrected Aridity: ERA5-FAO-PM vs gridMET"][
    "r_squared"
]
original_arid_rmse = validation_stats["Original Aridity: ERA5-FAO-PM vs gridMET"][
    "rmse"
]
corrected_arid_rmse = validation_stats[
    "Bias-Corrected Aridity: ERA5-FAO-PM vs gridMET"
]["rmse"]
original_arid_bias = validation_stats["Original Aridity: ERA5-FAO-PM vs gridMET"][
    "bias"
]
corrected_arid_bias = validation_stats[
    "Bias-Corrected Aridity: ERA5-FAO-PM vs gridMET"
]["bias"]

print("\nAridity:")
print(
    f"  R² improvement: {original_arid_r2:.3f} → {corrected_arid_r2:.3f} ({corrected_arid_r2 - original_arid_r2:+.3f})"
)
print(
    f"  RMSE change: {original_arid_rmse:.3f} → {corrected_arid_rmse:.3f} ({corrected_arid_rmse - original_arid_rmse:+.3f})"
)
print(
    f"  Bias reduction: {original_arid_bias:.3f} → {corrected_arid_bias:.3f} ({abs(corrected_arid_bias) - abs(original_arid_bias):+.3f})"
)

print(f"\n{'=' * 80}")

# %%
