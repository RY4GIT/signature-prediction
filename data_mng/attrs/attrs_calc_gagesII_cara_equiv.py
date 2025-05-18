# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# %%
attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
filename = "attrs_cara_gages2_etc_20250517.csv"


# %%
attrs = pd.read_csv(os.path.join(attrs_dir, filename))
attrs.head()


# %% ####################################
# Check drainage area discrepancy
########################################
attrs["delineation_err"] = (
    (attrs["area"] - attrs["DRAIN_SQKM"]) / attrs["DRAIN_SQKM"] * 100
)
attrs[["gauge_id", "delineation_err", "area", "DRAIN_SQKM"]][
    attrs["delineation_err"] > 25
].to_csv(os.path.join(attrs_dir, "delineation_err.csv"), index=False)

# %% ####################################
# PROTECTED AREA PERCENTAGE
########################################
#  Get protected area precent basin based on GAGES II datasets
attrs["PADCAT1_AND_2"] = attrs["PADCAT1_PCT_BASIN"] + attrs["PADCAT2_PCT_BASIN"]

# %% ####################################
# CLIMATE EQUIVALENTs
########################################
attrs["PET_mm_day"] = attrs["PET"] / 365  # mm/year to mm/day
attrs["P_mm_day"] = (attrs["PPTAVG_BASIN"] * 10) / 365  # cm/year to mm/day
attrs["ARIDITY_GAGES2"] = attrs["PET"] / (
    attrs["PPTAVG_BASIN"] * 10
)  # PET/P, convert both in mm/year
attrs["ARIDITY_GAGES2"].hist(bins=100)
attrs["SNOW_FRAC_PRECIP"] = attrs["SNOW_PCT_PRECIP"] / 100  # percent to fraction

# %% ####################################
# TERRAIN SLOPE EQUIVALENTs
########################################
attrs["SLOPE_DEG_x10"] = np.arctan(attrs["SLOPE_PCT"] / 100) * 180 / np.pi * 10

# %% ####################################
# CLIMATE EQUIVALENTs
########################################

# %%
attrs.to_csv(
    os.path.join(attrs_dir, filename),
    index=False,
)
# %%
# %% ######################################################
# Check some Caravan-GAGES2 equivalent attributes
# ######################################################


# Create a list of all attribute pairs to plot
attr_pairs = [
    ("slp_dg_sav", "SLOPE_DEG_x10", "Slope"),
    # ("soc_th_sav", "OMAVE", "Soil organic matter"),
    # ("hdi_ix_sav", "FRAGUN_BASIN", "Development index"),
    ("pet_mean_FAO_PM", "PET_mm_day", "PET"),
    ("aridity_FAO_PM", "ARIDITY_GAGES2", "Aridity"),
    # ("seasonality_FAO_PM", "PRECIP_SEAS_IND", "Seasonality"),
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
    ("frac_snow", "SNOW_FRAC_PRECIP", "Snow fraction"),
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

    axs[i].scatter(cara_var, gages2_var, s=1, alpha=0.5)

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
fig.savefig(os.path.join(attrs_dir, "figs", "all_attrs_comparison_attrsfile.png"))

# %%
