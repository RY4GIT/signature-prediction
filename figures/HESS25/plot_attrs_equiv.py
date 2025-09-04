# %% Get attribute sets for RF predictions (Most of the signatures, except Wu)
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# %% ____________________________________________________________
# Config

shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
derived_attrs_dir = os.path.join(shared_drive, "data", "derived_attrs", "assembled_RA")
fig_dir = os.path.join(shared_drive, "figs", "supfig_attrs_equiv")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# %% ######################################################
# Get the derived attributes, and filter out the ones not used in this study
# ######################################################

# Get the derived attributes of Caravan+GAGES2
file_name = "attrs_cara_gages2_etc_20250517+cluster"
attrs_file = os.path.join(derived_attrs_dir, file_name + ".csv")
attrs = pd.read_csv(attrs_file, index_col="gauge_id")

# Get the attributes of CAMELS
camels_attrs_file = os.path.join(derived_attrs_dir, "attrs_camels.csv")
camels_attrs = pd.read_csv(camels_attrs_file, index_col="gauge_id")

# Get attributes within the United States of America
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

# %% ######################################################
# Plot all attributes that converted/computed equivalent between Caravan and GAGES2
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
    ("pac_pc_sse", "PADCAT1_AND_2", "Protected areas"),
    ("cly_pc_sav", "CLAYAVE", "Clay"),
    ("slt_pc_sav", "SILTAVE", "Silt"),
    ("ppd_pk_sav", "PDEN_2000_BLOCK", "Population density"),
    ("p_mean", "P_mm_day", "Precipitation"),
    ("pet_mean_FAO_PM", "PET_mm_day", "PET"),
    ("aridity_FAO_PM", "ARIDITY_GAGES2", "Aridity"),
    ("frac_snow", "SNOW_FRAC_PRECIP", "Snow fraction"),
]

# Calculate number of rows and columns needed
n_plots = len(attr_pairs)
n_cols = 4
n_rows = (n_plots + n_cols - 1) // n_cols

# Create figure and subplots
fig, axs = plt.subplots(n_rows, n_cols, figsize=(11, 2.4 * n_rows))
axs = axs.flatten()
plt.rcParams.update({"font.size": 12})

# Plot each pair of attributes
for i, (cara_varname, gages2_varname, title) in enumerate(attr_pairs):
    cara_var = attrs[cara_varname]
    gages2_var = attrs[gages2_varname]

    # THESE EQUATIONS ARE USED BEFORE THE ATTRIBUTES ARE MERGED

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

    axs[i].scatter(cara_var, gages2_var, s=1, alpha=0.5)

    nan_mask = ~np.isnan(cara_var) & ~np.isnan(gages2_var)
    pearson_corr = np.corrcoef(cara_var[nan_mask], gages2_var[nan_mask])[0, 1]

    # Add 1:1 line
    lims = [
        min(min(cara_var), min(gages2_var)),
        max(max(cara_var), max(gages2_var)),
    ]
    if cara_varname == "slt_pc_sav":
        lims = [lims[0], 80]
    if cara_varname == "aridity_FAO_PM":
        lims = [0, 3]
    if cara_varname == "area":
        lims = [lims[0], 12000]
    axs[i].plot(lims, lims, "k--", alpha=0.3, zorder=0)

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
        fontsize=10,
    )

# Remove empty subplots if any
for i in range(len(attr_pairs), len(axs)):
    fig.delaxes(axs[i])


plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "all_attrs_comparison.png"), dpi=300)
