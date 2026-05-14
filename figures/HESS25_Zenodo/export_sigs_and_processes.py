# %% Plot signatures from multiple sources (Caravan, GAGES-II, RF predictions)
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings


# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")

# Google Drive directory
gdrive_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"

# Local directory (For Caravan data)
local_dir = r"D:\data"

# Output directory (For signatures results, change name to match the current run dates)
out_dir = os.path.join(gdrive_dir, "out", "signatures", "caravan_us_20250525")
out_dir_gages2 = os.path.join(gdrive_dir, "out", "signatures", "gages2_20250608")
rf_out_dir = os.path.join(gdrive_dir, "out", "rf", "output_raraki_20250826_cluster_all")

# fig_dir = os.path.join(
#     gdrive_dir,
#     "figs",
# )

zenodo_dir = os.path.join(gdrive_dir, "out", "zenodo", "data")
# Make Figure directory
if not os.path.exists(zenodo_dir):
    os.makedirs(zenodo_dir)

leaflet_json_dir = r"C:\Users\flipl\dev\ry4git.github.io\docs\assets\shp\sig_us"
if not os.path.exists(leaflet_json_dir):
    os.makedirs(leaflet_json_dir)

# Plotting config
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_sigs.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# Drop Wu signatures from the plot_sigs_config
plot_sigs_config = plot_sigs_config[
    ~plot_sigs_config["column_name"].isin(
        ["R_Pint_RC", "R_Pvol_RC", "diff_RCPint_RCPvol"]
    )
]

# Conus extent
conus_extent = [-125.5, -66.95, 24.396308, 47.5]


def sort_polygons_area_descending(gdf, equal_area_epsg=5070):
    """
    Sort by polygon area in an equal-area CRS (largest first, smallest last) so small
    watersheds draw on top in Leaflet. Returns GeoDataFrame in the original CRS.
    """
    out = gdf.copy()
    orig = out.crs if out.crs is not None else "EPSG:4326"
    out = out.to_crs(equal_area_epsg)
    out["_area_m2"] = out.geometry.area
    out = out.sort_values("_area_m2", ascending=False).drop(columns=["_area_m2"])
    out = out.to_crs(orig)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=orig)


# %%
# ____________________________________________________________________________________
# Load data
print("Loading attributes data...")

caravan_attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
attrs_camels_file = os.path.join(
    caravan_attrs_dir,
    "camels",
    "attributes_other_camels.csv",
)
attrs_hysets_file = os.path.join(
    caravan_attrs_dir,
    "hysets",
    "attributes_other_hysets.csv",
)
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
attrs_caravan = pd.concat([attrs_camels, attrs_hysets])

eco_camels_file = os.path.join(
    gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_camels.csv"
)
eco_hysets_file = os.path.join(
    gdrive_dir, "data", "derived_attrs", "EcoRegions", "Ecoregion_hysets.csv"
)
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])

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
    gdrive_dir, "data", "GAGES2", "GAGES_II_Geospa", "gages2_polygons_not_cara.shp"
)
gages2_wspolygon = gpd.read_file(gages2_wspolygon_file).to_crs(epsg=4326)
gages2_wspolygon["gauge_id"] = "gages2_" + gages2_wspolygon["GAGE_ID"].astype(
    str
).str.zfill(8)


# %%
print("Concatenating Caravan and GAGES2 watershed shapefiles...")
wspolygon = pd.concat(
    [
        wspolygon_camels,
        wspolygon_hysets,
        gages2_wspolygon.drop(columns=["PERIMETER", "GAGE_ID"]),
    ],
    ignore_index=True,
)
wspolygon.set_index("gauge_id", inplace=True)
wspolygon


# %%
def simplify_geometries(gdf, tolerance=0.01):
    """
    Simplifies the geometry of a GeoDataFrame for faster plotting.
    Args:
        gdf: GeoDataFrame with geometry column
        tolerance: Tolerance for simplification (degrees)
    Returns:
        GeoDataFrame with simplified geometries
    """
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    return gdf


wspolygon = simplify_geometries(wspolygon, tolerance=0.02)


# %% #######################################################
# Loading the data
############################################################
print("Loading signatures results file ...")

print("Loading signatures results file for Caravan ...")
_df_sigs_cara = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area.csv"),
    index_col="gauge_id",
)
_df_sigs_cara["source"] = "obs_Caravan"
_df_sigs_cara["order"] = 1
# %%
print("Loading signatures results file for GAGES2 ...")
_df_sigs_gages2 = pd.read_csv(
    os.path.join(out_dir_gages2, "out_calc_All_custom_filt_qc_snow.csv"),
)
_df_sigs_gages2["gauge_id"] = "gages2_" + _df_sigs_gages2["gauge_id"].astype(
    str
).str.zfill(8)
_df_sigs_gages2.set_index("gauge_id", inplace=True)
_df_sigs_gages2["source"] = "obs_GAGES2"
_df_sigs_gages2["order"] = 2
_df_sigs_gages2
# %%
print("Loading signatures results from RF predictions (overlap, baddata basins)...")
_df_sigs_rf_overlap_baddata = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_gg2_baddata.csv"),
    index_col="gauge_id",
)
# Pivot the dataframe to make signature names into columns
_df_sigs_rf_overlap_baddata = _df_sigs_rf_overlap_baddata.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_overlap_baddata["source"] = "pred_hys_gg2"
_df_sigs_rf_overlap_baddata["order"] = 3

print("Loading signatures results from RF predictions (only hys basins)...")
_df_sigs_rf_hys_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_hys_only = _df_sigs_rf_hys_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_hys_only["source"] = "pred_hys"
_df_sigs_rf_hys_only["order"] = 4

print("Loading signatures results from RF predictions (only GAGES2 basins)...")
_df_sigs_rf_gg2_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_gg2_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_gg2_only = _df_sigs_rf_gg2_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_gg2_only["source"] = "pred_gg2"
_df_sigs_rf_gg2_only["order"] = 5


# %%
# Add missing gages 2 info
gg2_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat+climate.csv"
gg2_attrs = pd.read_csv(gg2_attrs_file)
gg2_attrs.columns
# %%
gg2_attrs["gauge_id"] = "gages2_" + gg2_attrs["STAID"].astype(str).str.zfill(8)
# gg2_attrs["country"] = "United States of America"
gg2_attrs["gauge_name"] = gg2_attrs["STANAME"]
gg2_attrs["gauge_lat"] = gg2_attrs["LAT_GAGE"]
gg2_attrs["gauge_lon"] = gg2_attrs["LNG_GAGE"]
gg2_attrs["area"] = gg2_attrs["DRAIN_SQKM"]
gg2_attrs["gauge_num"] = gg2_attrs["STAID"].astype(str).str.zfill(8)
gg2_attrs.set_index("gauge_id", inplace=True)
# gg2_attrs = gg2_attrs.dropna(subset=["gauge_name"])
# %%
gg2_attrs.loc["gages2_14212000"]
# attrs_caravan = attrs_caravan.join(eco_caravan)
# %%
# attrs_caravan
# %%
sel_col = [
    "gauge_name",
    # "country",
    "gauge_lat",
    "gauge_lon",
    "area",
]
attrs = pd.concat(
    [
        attrs_caravan[sel_col],
        gg2_attrs[sel_col],
    ],
    axis=0,
)
attrs.rename(columns={"area": "area_km2"}, inplace=True)
attrs
# %%
print("Concatenating signatures results...")
_df_sigs = pd.concat(
    [
        _df_sigs_cara,
        _df_sigs_gages2,
        _df_sigs_rf_overlap_baddata,
        _df_sigs_rf_hys_only,
        _df_sigs_rf_gg2_only,
    ]
)
_df_sigs = _df_sigs.drop(
    columns=["gauge_name", "gauge_num", "country", "gauge_lat", "gauge_lon", "area"]
)


# %%
df_sigs = _df_sigs.join(
    attrs,
    how="left",
)
df_sigs
# %%
df_sigs["gauge_num"] = df_sigs.index.str.split("_").str[1]
df_sigs
# %%
# Join the watershed polygons to the signatures data
df_sigs = wspolygon.join(df_sigs, how="right", lsuffix="", rsuffix="_wspolygon")

# %%
#######################################################
# Preprocess the data
#######################################################

# Calcaulte some signatures
# df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["avg_IE_SE_thresh"] = (df_sigs["IE_thresh"] + df_sigs["SE_thresh"]) / 2
df_sigs["avg_IE_SE_signif"] = (
    df_sigs["IE_thresh_signif"] + df_sigs["SE_thresh_signif"]
) / 2
df_sigs["avg_IE_SE_thresh"].iloc[df_sigs["avg_IE_SE_thresh"] > 300] = np.nan
# %%
# Mask out gauges with high snow
frac_snow_thresh = 0.2
low_snow = (
    (df_sigs["SNOW_PCT_PRECIP"] < frac_snow_thresh * 100)
    | (df_sigs["SNOW_PCT_PRECIP"].isna())
) | ((df_sigs["SNOWICENLCD06"] < frac_snow_thresh) | (df_sigs["SNOWICENLCD06"].isna()))
mask_cols = [
    "IE_thresh",
    "SE_thresh",
    "Storage_thresh",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "Storage_thresh_signif",
]
df_sigs[mask_cols] = df_sigs[mask_cols].mask(~low_snow)
# This line replaces values with NaN for any rows where low_snow is False
# low_snow is True for gauges with snow < threshold, False otherwise
# So ~low_snow is True for gauges with high snow, which get masked to NaN

print(
    f"{df_sigs['IE_thresh'].isna().sum()} gauges ({df_sigs['IE_thresh'].isna().sum() / len(df_sigs) * 100:.1f}%) have snow data above {frac_snow_thresh * 100}%"
)
# %%
print("Data length: ", len(df_sigs))
print("Baseflow data length: ", len(df_sigs[df_sigs["BFI"].notna()]))
print("Overlandflow data length: ", len(df_sigs[df_sigs["IE_thresh"].notna()]))


# %%
# Get the percentile
def below_thresh_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


for sigs_name in plot_sigs_config["column_name"]:
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    if "_signif" in sigs_name:
        df_sigs[sigs_name + "_perc"] = below_thresh_percentile(df_sigs[sigs_name], 0.05)
    else:
        df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100


# %%
########################################################################################
# Functions
########################################################################################
# Get quantile & bivariate classes of data
def get_bivariate_class(df, sig1, sig2, sig1_label, sig2_label):
    df_clean = df.dropna(subset=[sig1.column_name, sig2.column_name]).copy()

    # Use custom bins for percentile columns
    for sig, label in [(sig1, sig1_label), (sig2, sig2_label)]:
        col_name = sig.column_name
        class_col = col_name + "_class"

        if "_perc" in col_name:
            # Use fixed percentile bins (0, 25, 50, 75, 100) for percentile columns
            # Already in percentiles, so use fixed bins
            bins = [0, 25, 50, 75, 100]
            df_clean[class_col] = pd.cut(
                df_clean[col_name], bins=bins, labels=label, include_lowest=True
            )
        else:
            # Use quantile-based binning for non-percentile columns
            # Not in percentiles, so use quantiles
            df_clean[class_col] = pd.qcut(
                df_clean[col_name], q=len(label), labels=label
            )

    df_clean["bivariate_class"] = (
        df_clean[sig1.column_name + "_class"].astype(str)
        + "-"
        + df_clean[sig2.column_name + "_class"].astype(str)
    )

    df_clean["color"] = df_clean["bivariate_class"].apply(
        lambda x: patch_colors[int(x.split("-")[1]) - 1][int(x.split("-")[0]) - 1]
    )

    return df_clean


def plot_bivariate_map(df, sig1, sig2, fig_dir, plot_mode="polygon"):
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

    # Add map features
    if plot_mode == "scatter":
        ax.scatter(
            df["gauge_lon"],
            df["gauge_lat"],
            color=df["color"],
            marker="o",
            s=5,
            alpha=0.5,
            zorder=99,
        )
    elif plot_mode == "polygon":
        # Add an area column (if not already present)
        df["area"] = df.geometry.area

        # Sort by area in descending order so smaller polygons are plotted last
        df.sort_values("area", ascending=False, inplace=True)

        # Plot the polygons
        df.plot(
            ax=ax,
            color=df["color"],
            linewidth=0.2,
            alpha=0.4,
            zorder=99,
        )

    ax.set_extent(conus_extent)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Output directory
    fig_bivar_dir = os.path.join(fig_dir, "fig_processes")
    if not os.path.exists(fig_bivar_dir):
        os.makedirs(fig_bivar_dir)

    # Display the plot
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            fig_bivar_dir,
            f"bivar_{sig1.column_name}_{sig2.column_name}_{plot_mode}.png",
        ),
        dpi=300,
    )


def update_column_name(signal):
    """
    Updates the column_name attribute of the signal to use percentile, if it is threshold-based signatures
    Parameters:
    - signal: An object with `label` and `column_name` attributes.
    """
    label_to_column = {
        "IE_thresh_signif": "IE_thresh_signif_perc",
        "SE_thresh_signif": "SE_thresh_signif_perc",
        "Storage_thresh_signif": "Storage_thresh_signif_perc",
        "avg_IE_SE_signif": "avg_IE_SE_signif_perc",
    }
    if signal.column_name in label_to_column:
        signal.column_name = label_to_column[signal.column_name]
        signal.label = signal.label.replace("(p-value)", "significance")


# ______________________________________________________
# Preparation, do not change here
patch_colors = [
    ["#D3D3D3", "#D6B3A0", "#D9926A", "#DD6A29"],
    ["#9CC4D2", "#9EA69F", "#A08769", "#A36229"],
    ["#5FB2D1", "#60979F", "#617B69", "#635929"],
    ["#159DD0", "#15869E", "#176D68", "#174F28"],
]
cmap = ListedColormap(patch_colors)

# Labels for quantiles (low-->high)
labels = [1, 2, 3, 4]
dir_label = ["low", "", "", "high"]

# Reversed labels for quantiles (high --> low)
labels_rev = [
    4,
    3,
    2,
    1,
]
# Label low values as 4, so that it gets assinged to (x,y)=(i,4) or (4,j) in the quadrant
dir_label_rev = ["high", "", "", "low"]


# End of "do not change"
# ______________________________________________________

# %% ########################################################################################
#
# Plot the bivariate map of the processes
#
########################################################################################

processes = [
    "Baseflow",
    "High storage capacity",
    "Water balance losses",
    "Seasonal variability",
    "Overland Flow",
]

# df_sigs_clean = pd.DataFrame()
for process_name in tqdm(
    processes, desc="Exporting bivariate classes of process hypothesis", leave=False
):
    # For checking the items
    process_columns = plot_sigs_config[plot_sigs_config["process"] == process_name]
    print(process_columns)

    ###############################
    # Get the process signatures
    ###############################

    # For Baseflow plots
    if process_name == "Baseflow":
        sig2 = process_columns[
            process_columns["column_name"] == "BFI"
        ].squeeze()  # Y variable, BFI
        sig1 = process_columns[
            process_columns["column_name"] == "BaseflowRecessionK"
        ].squeeze()  # X variable, Baseflow Recession K

        sig1_label = labels
        sig2_label = labels

        sig1_dir = dir_label
        sig2_dir = dir_label

        keep_columns_sig = [
            "BFI",
            "BFI_perc",
            "BaseflowRecessionK",
            "BaseflowRecessionK_perc",
        ]

    ###############################
    # For Staoge capacity and retention

    if process_name == "High storage capacity":
        sig1 = process_columns[
            process_columns["column_name"] == "RecessionParameters_b"
        ].squeeze()  # X variable, RecessionParameters_b
        sig2 = process_columns[
            process_columns["column_name"] == "AverageStorage"
        ].squeeze()  # Y variable, AverageStorage

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        # Higher b (=high nonlinearity) means multiple storages, so reverse the direction
        sig2_dir = dir_label

        keep_columns_sig = [
            "RecessionParameters_b",
            "RecessionParameters_b_perc",
            "AverageStorage",
            "AverageStorage_perc",
        ]

    ###############################
    # For Water loss to deep GW or ET
    if process_name == "Water balance losses":
        sig2 = process_columns[
            process_columns["column_name"] == "TotalRR"
        ].squeeze()  # Y variable, Total RR
        sig1 = process_columns[
            process_columns["column_name"] == "EventRR"
        ].squeeze()  # X variable, EventRR

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

        keep_columns_sig = [
            "TotalRR",
            "TotalRR_perc",
            "EventRR",
            "EventRR_perc",
        ]

    ###############################

    # For ET impacts on storage and baseflow
    if process_name == "Seasonal variability":
        sig1 = process_columns.loc[
            process_columns.column_name == "VariabilityIndex"
        ].squeeze()  # X variable, VariabilityIndex
        sig2 = process_columns.loc[
            process_columns.column_name == "Recession_a_Seasonality"
        ].squeeze()  # Y variable,

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

        keep_columns_sig = [
            "VariabilityIndex",
            "VariabilityIndex_perc",
            "Recession_a_Seasonality",
            "Recession_a_Seasonality_perc",
        ]

    ###############################
    # For Overland Flow
    if process_name == "Overland Flow":
        sig1 = process_columns.loc[
            process_columns.column_name == "avg_IE_SE_signif"
        ].squeeze()  # X variable
        sig2 = process_columns.loc[
            process_columns.column_name == "avg_IE_SE_thresh"
        ].squeeze()  # Y variable

        sig1_label = labels_rev
        sig2_label = labels

        sig1_dir = dir_label_rev
        sig2_dir = dir_label

        keep_columns_sig = [
            "avg_IE_SE_signif",
            "avg_IE_SE_signif_perc",
            "avg_IE_SE_thresh",
            "avg_IE_SE_thresh_perc",
            "SE_thresh_signif",
            "SE_thresh_signif_perc",
            "IE_thresh_signif",
            "IE_thresh_signif_perc",
            "IE_thresh",
            "IE_thresh_perc",
            "SE_thresh",
            "SE_thresh_perc",
        ]

    # If looking at the significance of the threshold values,
    # use the percentile columns, instead of the original p-values
    update_column_name(sig1)
    update_column_name(sig2)

    print(
        f"Processing the bivariate classification for Y: {sig2.column_name} & X: {sig1.column_name}"
    )

    #####################################################
    # Plot the bivariate map
    #####################################################

    # Get the bivariate class of data
    _df_sigs_clean = get_bivariate_class(
        df_sigs, sig1, sig2, sig1_label, sig2_label
    ).copy()
    _df_sigs_clean["bivariate_class"] = _df_sigs_clean["bivariate_class"].astype(str)

    #######################################################
    # Dominance
    ########################################################

    if process_name == "Water balance losses":
        class_list = ["4-1", "3-1", "3-2", "4-2"]
    else:
        class_list = ["1-4", "1-3", "2-3", "2-4"]
    _df_sigs_clean["dominance"] = _df_sigs_clean["bivariate_class"].isin(class_list)

    #######################################################
    # output as csv
    ########################################################
    _df_sigs_clean["gauge_num"] = (
        _df_sigs_clean.index.str.split("_").str[1].astype(str).str.zfill(8)
    )
    _df_sigs_clean["gauge_id"] = _df_sigs_clean.index.astype(str)

    keep_columns_base = [
        "gauge_id",
        "gauge_num",
        # "gauge_num_wspolygon",
        "gauge_name",
        "gauge_lat",
        "gauge_lon",
        # "area",
        # "ecoregion",
        "bivariate_class",
        "dominance",
        "color",
        "source",
        "order",
    ]

    keep_columns = keep_columns_base + keep_columns_sig

    process_stem = "".join([word.capitalize() for word in process_name.split()])
    out_filename = f"sigs_{process_stem}.csv"
    _df_sigs_clean[keep_columns].to_csv(os.path.join(zenodo_dir, out_filename))

    #######################################################
    # output as geojson
    ########################################################

    keep_columns_base = [
        "gauge_id",
        "gauge_num",
        "geometry",
        "gauge_name",
        "bivariate_class",
        "dominance",
        "color",
        "source",
        "order",
    ]

    if process_name == "Overland Flow":
        keep_columns_sig_geo = [
            "avg_IE_SE_signif",
            "avg_IE_SE_signif_perc",
            "avg_IE_SE_thresh",
            "avg_IE_SE_thresh_perc",
        ]
    else:
        keep_columns_sig_geo = keep_columns_sig

    keep_columns = keep_columns_base + keep_columns_sig_geo

    _gjson = _df_sigs_clean[keep_columns].copy()
    # Avoid "cannot insert gauge_id, already exists" (index name + column both gauge_id)

    # Order by area
    _gjson = sort_polygons_area_descending(_gjson)

    #
    _gjson = _gjson.reset_index(drop=True)
    _gjson = gpd.GeoDataFrame(
        _gjson,
        geometry="geometry",
        crs=df_sigs.crs if df_sigs.crs is not None else "EPSG:4326",
    )
    _gjson.to_file(
        os.path.join(leaflet_json_dir, f"sigs_{process_stem}.geojson"),
        driver="GeoJSON",
    )

#######################################################
# output the gauge point
########################################################
keep_columns_base = [
    # "gauge_id",
    "gauge_num",
    "gauge_lat",
    "gauge_lon",
    # "geometry",
    # "bivariate_class",
    # "dominance",
    # "color",
    # "source",
    # "order",
]
df_pts = df_sigs[keep_columns_base].copy()
# Subset without the polygon geometry column is a plain DataFrame; to_file needs GeoDataFrame.
df_pts = gpd.GeoDataFrame(
    df_pts,
    geometry=gpd.points_from_xy(df_pts["gauge_lon"], df_pts["gauge_lat"]),
    crs="EPSG:4326",
)
df_pts.to_file(
    os.path.join(leaflet_json_dir, "gauge_pts.json"),
    driver="GeoJSON",
)

# %%
