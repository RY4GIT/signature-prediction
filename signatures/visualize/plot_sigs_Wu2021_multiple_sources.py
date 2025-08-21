# %%
import os
import pandas as pd
import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %% #######################################
# Config
############################################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
sig_dir = os.path.join(cloud_dir, "out", "signatures", "Wu_sigs_20250812")
rf_dir = os.path.join(cloud_dir, "out", "rf", "output_raraki_20250820_cluster_all_Wu")
local_dir = r"D:\data"
fig_dir = sig_dir

conus_extent = [-125.5, -66.95, 24.396308, 47.5]

# %% #######################################
# Load datasets
############################################
print("Loading signatures results file ...")


def load_sigs_obs(file_path):
    df_sigs = pd.read_csv(file_path)
    if "gauge_num" in df_sigs.columns:
        df_sigs["gauge_num"] = df_sigs["gauge_num"].astype(str).str.zfill(8)
        df_sigs["gauge_id"] = df_sigs["data_name"] + "_" + df_sigs["gauge_num"]
    else:
        df_sigs["gauge_num"] = df_sigs["gauge_id"].str.split("_").str[1]
    df_sigs.set_index("gauge_id", inplace=True)
    # Pivot long-to-wide if needed: columns become signature names, values are predictions
    if "sig_name" in df_sigs.columns and "prediction" in df_sigs.columns:
        meta_columns = [
            c for c in df_sigs.columns if c not in ["sig_name", "prediction"]
        ]
        meta_per_gauge = df_sigs.groupby(level=0)[meta_columns].first()
        wide_values = df_sigs.pivot_table(
            index=df_sigs.index,
            columns="sig_name",
            values="prediction",
            aggfunc="first",
        )
        wide_values.columns.name = None
        df_sigs = meta_per_gauge.join(wide_values)
    return df_sigs


print("Loading observed signatures results file for Caravan ...")
sigs_obs_cara = load_sigs_obs(
    os.path.join(sig_dir, "out_sigEvent_cara_gg2_rf_train.csv")
)
print(f"Number of Caravan gauges in sigs_obs_cara: {len(sigs_obs_cara)}")
sigs_obs_cara.head()
# %%
print("Loading observed signatures results file for GAGES2 ...")
_sigs_obs_gg2 = load_sigs_obs(
    os.path.join(sig_dir, "out_sigEvent_cara_gg2_no_duplicates.csv")
)
sigs_obs_gg2 = _sigs_obs_gg2[_sigs_obs_gg2["data_name"] == "gages2"].copy()
print(f"Number of GAGES2 gauges in sigs_obs_gg2: {len(sigs_obs_gg2)}")
sigs_obs_gg2.head()
# TDOO:
# %%
print("Loading predicted signatures results files ...")
sigs_pred_gg2 = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_gg2_only_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_gg2: {len(sigs_pred_gg2)}")
sigs_pred_gg2["data_name"] = "pred_gg2"
sigs_pred_gg2.head()
# %%
sigs_pred_hys_gg2 = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_hys_gg2_baddata_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_hys_gg2: {len(sigs_pred_hys_gg2)}")
sigs_pred_hys_gg2["data_name"] = "pred_hys_gg2"
sigs_pred_hys_gg2.head()
# %%
sigs_pred_hys = load_sigs_obs(
    os.path.join(rf_dir, "predicted_signatures_pred_hys_only_Wu.csv")
)
print(f"Number of GAGES2 gauges in sigs_pred_hys: {len(sigs_pred_hys)}")
sigs_pred_hys["data_name"] = "pred_hys"
sigs_pred_hys.head()


# %%
print("Loading Caravan watershed shapefiles...")
# cARAVAN 1.5 shapefile is somehow corrupted, so use Caravan 1.4
wspolygon_camels_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "camels", "camels_basin_shapes.shp"
)
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "hysets", "hysets_basin_shapes.shp"
)
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
# %%
print("Loading GAGES2 watershed shapefiles...")
gages2_wspolygon_file = os.path.join(
    cloud_dir, "data", "GAGES2", "GAGES_II_Geospa", "gages2_polygons_not_cara.shp"
)
gages2_wspolygon = gpd.read_file(gages2_wspolygon_file).to_crs(epsg=4326)
gages2_wspolygon["gauge_id"] = "gages2_" + gages2_wspolygon["GAGE_ID"].astype(
    str
).str.zfill(8)

# %%
print("Loading Caravan attributes...")
cara_attrs_path = os.path.join(
    cloud_dir,
    "data",
    "derived_attrs",
    "assembled_RA",
    "attrs_cara_gages2_etc_20250517+cluster.csv",
)
cara_attrs = pd.read_csv(cara_attrs_path, index_col=0)

# %%
print("Loading GAGES2 attributes...")
gages2_attrs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
gages2_attrs = pd.read_csv(gages2_attrs_path)
gages2_attrs["gauge_id"] = "gages2_" + gages2_attrs["STAID"].astype(str).str.zfill(8)
gages2_attrs.set_index("gauge_id", inplace=True)


# %%
print("Concatenating Caravan and GAGES2 signatures and watershed shapefiles...")
sigs = pd.concat(
    [sigs_obs_cara, sigs_obs_gg2, sigs_pred_gg2, sigs_pred_hys_gg2, sigs_pred_hys],
    axis=0,
)
print(f"Number of gauges in sigs: {len(sigs)}")

wspolygon = pd.concat(
    [
        wspolygon_camels,
        wspolygon_hysets,
        gages2_wspolygon.drop(columns=["AREA", "PERIMETER", "GAGE_ID", "usgs_gauge"]),
    ],
    ignore_index=True,
)
wspolygon.set_index("gauge_id", inplace=True)

if "gauge_id" in sigs.columns:
    sigs.set_index("gauge_id", inplace=True)
sigs = sigs.join(wspolygon, how="left")

print("Joining Caravan attributes...")
sigs = sigs.join(cara_attrs, how="left")
print(f"Number of gauges in sigs: {len(sigs)}")
sigs.tail()

print("Joining GAGES2 attributes...")
sigs = sigs.join(gages2_attrs, how="left", lsuffix="", rsuffix="_gages2")
print(f"Number of gauges in sigs: {len(sigs)}")

sigs.tail()
# %%
print("Curating data...")
sigs = gpd.GeoDataFrame(sigs, geometry="geometry", crs=4326)
sigs["area"] = sigs.geometry.values.area
sigs = sigs.sort_values(by="order", ascending=True)
sigs = sigs.sort_values(by="area", ascending=True)

# Calculate signature statistics
sigs["diff_RCPint_RCPvol"] = sigs["R_Pint_RC"] - sigs["R_Pvol_RC"]
# Mask where both R_Pint_RC and R_Pvol_RC are negative
sigs["diff_RCPint_RCPvol_masked"] = sigs["diff_RCPint_RCPvol"].mask(
    (sigs["R_Pint_RC"] < 0) & (sigs["R_Pvol_RC"] < 0)
)
# %%
# %% #######################################
# Filter out gauges with snow data below a threshold
############################################
frac_snow_thresh = 0.2
sigs_filt = sigs[
    (
        (sigs["SNOW_PCT_PRECIP"] < frac_snow_thresh * 100)
        & (~sigs["SNOW_PCT_PRECIP"].isna())
    )
    | (
        (sigs["SNOW_FRAC_PRECIP"] < frac_snow_thresh)
        & (~sigs["SNOW_FRAC_PRECIP"].isna())
    )
    | ((sigs["SNOWICENLCD06"] < frac_snow_thresh) & (~sigs["SNOWICENLCD06"].isna()))
    | (
        (sigs["SNOW_PCT_PRECIP_gages2"] < frac_snow_thresh * 100)
        & (~sigs["SNOW_PCT_PRECIP_gages2"].isna())
    )
    | (
        (sigs["SNOWICENLCD06_gages2"] < frac_snow_thresh)
        & (~sigs["SNOWICENLCD06_gages2"].isna())
    )
]
print(
    f"Number of gauges in sigs_filt: {len(sigs_filt)} ({len(sigs_filt) / len(sigs) * 100:.1f}%)"
)
sigs_filt

# %% #######################################
# Plot signatures
############################################
# Plot R_Pint_RC and R_Pvol_RC and diff_RCPint_RCPvol_masked
for sig_name in [
    "R_Pint_RC",
    "R_Pvol_RC",
    "diff_RCPint_RCPvol_masked",
]:
    # Set up the map
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add the BORDERS feature first
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="k")

    # Add the land feature with edgecolor set to black
    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
    )
    ax.add_feature(
        land,
        facecolor="#F4F5FA",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=1.0,  # Optionally adjust linewidth for edges
    )

    c_data = sigs[sig_name]
    cbar_label = "[-]"
    out_file_name = f"map_{sig_name}.png"

    if "diff_RCPint_RCPvol" in sig_name:
        diagonal_colors = [
            "#159DD0",
            # "#2CA6D4",
            # "#43B0D9",
            "#aeb5b1",
            # "#E38753",
            # "#E0783E",
            "#DD6A29",  #    or # DD6A29
        ]

        # diagonal_colors = [
        #     # "#2CA6D4",
        #     # "#43B0D9",
        #     "#aeb5b1",
        #     "#98B2B5",
        #     "#159DD0",
        #     # "#E38753",
        #     # "#E0783E",
        #     # "#DD6A29", #    or # DD6A29
        # ]

        # Create the colormap
        diag_cmap = LinearSegmentedColormap.from_list(
            "custom_diag_gradient", diagonal_colors
        )

        cmap = diag_cmap
        vmin = -0.1
        vmax = 0.1
    else:
        cmap = "viridis"
        vmin = -0.5
        vmax = 1

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    # Drop where geometry is nan
    sigs_plot = sigs_filt[sigs_filt.geometry.notna()].copy()

    # Plot the signature data
    sigs_plot.plot(
        ax=ax,
        column=sig_name,
        cmap=cmap,
        norm=norm,
        linewidth=0.2,
        alpha=0.5,
        vmin=vmin,
        vmax=vmax,
        zorder=99,
    )

    # Add a colorbar
    if "diff_RCPint_RCPvol" in sig_name:
        # Save colorbar to a separate file (no colorbar on the map)
        sm_cb = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm_cb.set_array([])
        fig_cb = plt.figure(figsize=(2, 3), constrained_layout=True)
        ax_cb = fig_cb.add_subplot(111)
        ax_cb.set_axis_off()
        cb = fig_cb.colorbar(sm_cb, ax=ax_cb, orientation="vertical")
        cb.set_ticks(np.linspace(vmin, vmax, 5))
        cb.ax.tick_params(labelsize=18)
        cb.set_label(cbar_label, rotation=270, labelpad=30, fontsize=18)
        fig_cb.savefig(
            os.path.join(fig_dir, f"colorbar_{sig_name}.pdf"),
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.2,
        )
        plt.close(fig_cb)
    else:
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []  # Empty array for ScalarMappable
        cbar = plt.colorbar(sm, ax=ax, shrink=0.3)
        cbar.ax.tick_params(labelsize=18)  # Set font size
        cbar.set_ticks(np.linspace(vmin, vmax, 5))
        cbar.set_label(cbar_label, rotation=270, labelpad=30, fontsize=18)

    # ax.set_title(title_label)
    ax.set_extent(conus_extent)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(fig_dir, out_file_name), dpi=300)


# %%
