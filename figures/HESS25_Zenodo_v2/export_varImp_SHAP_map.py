# %%
import pandas as pd
import os
import json
import geopandas as gpd

# %%
########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
rf_out_dir = os.path.join(rf_dir, "output_raraki_20250826_cluster_all")
rf_out_dir_Wu = os.path.join(rf_dir, "output_raraki_20250827_cluster_all_Wu")
fig_dir = os.path.join(cloud_dir, "figs", "fig_varImp")
sfig_dir = os.path.join(cloud_dir, "figs", "supfig_varImp")
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)
if not os.path.exists(sfig_dir):
    os.makedirs(sfig_dir)

# ____________________________________________________________________________________
# Plot configs

# Attributes info & colors
config_attrs_info_file = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_attrs_info.csv"
)
attrs_info = pd.read_csv(config_attrs_info_file)
with open(
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_attrs_colors_high_contrast.json",
    "r",
) as file:
    attrs_colors = json.load(file)

# Signature info
sigs_RF_names_ordered = [
    "BFI",
    "BaseflowRecessionK",
    "AverageStorage",
    "RecessionParameters_b",
    "TotalRR",
    "EventRR",
    "Recession_a_Seasonality",
    "VariabilityIndex",
    "IE_thresh",
    "IE_thresh_signif",
    "SE_thresh",
    "SE_thresh_signif",
    "R_Pint_RC",
    "R_Pvol_RC",
]
sig_Wu_names = [
    "R_Pint_RC",
    "R_Pvol_RC",
]


# %%
# ____________________________________________________________________________________
# load CAMELS and HYSETS attributes

caravan_attrs_dir = r"D:\data\Caravan1.4\attributes"
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

attrs_camels = pd.read_csv(attrs_camels_file)
attrs_hysets = pd.read_csv(attrs_hysets_file)
attrs_camels["gauge_id"] = attrs_camels["gauge_id"].astype(str)
attrs_hysets["gauge_id"] = attrs_hysets["gauge_id"].astype(str)

# %%
print("Loading Caravan watershed shapefiles...")


# cARAVAN 1.5 shapefile is somehow corrupted, so use Caravan 1.4
local_dir = r"D:\data"
wspolygon_camels_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "camels", "camels_basin_shapes.shp"
)
wspolygon_camels = gpd.read_file(wspolygon_camels_file).to_crs(epsg=4326)
wspolygon_hysets_file = os.path.join(
    local_dir, "Caravan1.4", "shapefiles", "hysets", "hysets_basin_shapes.shp"
)
wspolygon_hysets = gpd.read_file(wspolygon_hysets_file).to_crs(epsg=4326)
wspolygon = pd.concat([wspolygon_camels, wspolygon_hysets]).set_index("gauge_id")


# %% ###################################################
# SHAP values
#######################################################

# %% #########################################################
# Load SHAP data
#############################################################

# Combine the SHAP results from all signatures
_df_shap_Wu = pd.read_csv(os.path.join(rf_out_dir_Wu, "shap_values.csv"))
_df_shap = pd.read_csv(os.path.join(rf_out_dir, "shap_values.csv"))
_df_shap = _df_shap[~_df_shap["sig_name"].isin(sig_Wu_names)]
df_shap = pd.concat([_df_shap, _df_shap_Wu], axis=0)


# %% Check if the gauge_id overlaps btween _df_shap_Wu and _df_shap
gauge_id_Wu = _df_shap_Wu["gauge_id"].unique()
gauge_id = df_shap["gauge_id"].unique()

print(gauge_id_Wu)
print(gauge_id)

print(len(gauge_id_Wu))
print(len(gauge_id))
print("Overlap:")
print(len(set(gauge_id_Wu) & set(gauge_id)))
print("Only in Wu:")
print(len(set(gauge_id_Wu) - set(gauge_id)))
print("Only in all:")
print(len(set(gauge_id) - set(gauge_id_Wu)))


# Make sure the data is float
df_shap["feature_value"] = df_shap["feature_value"].astype(float)
df_shap["phi"] = df_shap["phi"].astype(float)
df_shap["phi.var"] = df_shap["phi.var"].astype(float)
df_shap = df_shap.merge(
    attrs_info, how="left", left_on="feature", right_on="variable_name"
)
print(len(df_shap))
df_shap.tail()

# Get the sum for phi_abs per lopcatino and add it to the dataframe
df_shap["phi_abs"] = df_shap["phi"].abs()
df_shap["phi_abs_sum"] = df_shap.groupby("gauge_id")["phi_abs"].transform("sum")
df_shap["phi_perc"] = df_shap["phi"] / df_shap["phi_abs_sum"] * 100
df_shap["phi_abs_perc"] = df_shap["phi_abs"] / df_shap["phi_abs_sum"] * 100

# Join df_SHAP with attrs_camels and attrs_hysets on gauge_id
print("Joining SHAP data with attrs_camels and attrs_hysets...")
df_shap_camels = df_shap.merge(attrs_camels, how="right", on="gauge_id")
df_shap_hysets = df_shap.merge(attrs_hysets, how="right", on="gauge_id")
df_shap_with_attrs = pd.concat([df_shap_camels, df_shap_hysets])

print(len(df_shap_with_attrs))


# %% ###################################################
# PLOT SHAP IN A MAP
########################################################

# %% ###############################################################
# Get the average contributions from 2 signatures and plot the max category per location
########################################################
sig_pairs = {
    0: {"Process": "Baseflow", "sigs": ["BFI", "BaseflowRecessionK"]},
    1: {
        "Process": "High storage capacity",
        "sigs": ["AverageStorage", "RecessionParameters_b"],
    },
    2: {"Process": "Water balance losses", "sigs": ["EventRR", "TotalRR"]},
    3: {
        "Process": "Seasonal variability",
        "sigs": ["Recession_a_Seasonality", "VariabilityIndex"],
    },
    4: {
        "Process": "Overland flow",
        "sigs": ["IE_thresh", "IE_thresh_signif", "SE_thresh", "SE_thresh_signif"],
    },
    5: {
        "Process": "Overland flow threshold",
        "sigs": ["IE_thresh", "SE_thresh"],
    },
    6: {
        "Process": "Overland flow significance",
        "sigs": ["IE_thresh_signif", "SE_thresh_signif"],
    },
    7: {
        "Process": "Overland flow type",
        "sigs": ["R_Pint_RC", "R_Pvol_RC"],
    },
    8: {
        "Process": "All processes",
        "sigs": sigs_RF_names_ordered,
    },
}
# %% Get the stats per process per category
df_groups = []
for pair in sig_pairs.values():
    print(pair["Process"])
    print(pair["sigs"])
    print("--------------------------------")
    # _______________________________________________________________________
    # PREPARE THE DATA
    # Get the data for this signature

    for sig_name in pair["sigs"]:
        # Get the data for this signature
        df_shap_sig = df_shap_with_attrs[
            df_shap_with_attrs["sig_name"] == sig_name
        ].copy()

        # _______________________________________________________________________
        # Get mean phi_abs_perc per category for the signature and create a grouped dataframe
        df_group = (
            df_shap_sig.groupby(["Group", "gauge_id"])
            .agg(
                mean_phi_abs_perc=("phi_abs_perc", "mean"),
                gauge_lon=("gauge_lon", "first"),
                gauge_lat=("gauge_lat", "first"),
            )
            .reset_index()
        )
        df_group["Process"] = pair["Process"]

        df_groups.append(df_group)

    # _______________________________________________________________________
    # Get the average contributions from 2 signatures
    df_group_all = pd.concat(df_groups)

print(df_group_all["Process"].unique())


# %%

process_list = [
    "All processes",
    "Baseflow",
    "High storage capacity",
    "Water balance losses",
    "Seasonal variability",
    "Overland flow",
    "Overland flow threshold",
    "Overland flow significance",
    "Overland flow type",
    "All processes",
]
list_group_avg_max = []
for process in process_list:
    print(process)
    # _______________________________________________________________________
    df_group_all_process = df_group_all[df_group_all["Process"] == process]
    if process == "All processes":
        # This includes 14 signatures, so the median is more robust
        stats = "median"
    else:
        # This includes around 2 signatures, so the mean is more robust
        stats = "mean"

    # _______________________________________________________________________
    # Get the max category per location
    # Use the process name as sig_name for plotting

    # Recalculate mean after adding sig_name
    df_group_avg = (
        df_group_all_process.groupby(["gauge_id", "Group"])
        .agg(
            mean_phi_abs_perc=("mean_phi_abs_perc", stats),
            gauge_lon=("gauge_lon", "first"),
            gauge_lat=("gauge_lat", "first"),
            process=("Process", "first"),
            count=("mean_phi_abs_perc", "count"),
        )
        .reset_index()
    ).rename(columns={"mean_phi_abs_perc": f"{stats}_phi_abs_perc"})
    df_group_avg["Process"] = process

    # For each gauge_id, get the row with the maximum phi_abs_perc
    _df_group_avg_max = (
        df_group_avg.loc[
            df_group_avg.groupby("gauge_id")[f"{stats}_phi_abs_perc"].idxmax()
        ][
            [
                "gauge_id",
                f"{stats}_phi_abs_perc",
                "Group",
                "gauge_lon",
                "gauge_lat",
                "count",
                "process",
            ]
        ]
        .rename(
            columns={
                f"{stats}_phi_abs_perc": f"max_{stats}_phi_abs_perc",
                "Group": "Group_max",
            }
        )
        .reset_index(drop=True)
    )

    _df_group_avg_max["color"] = _df_group_avg_max["Group_max"].map(attrs_colors)

    list_group_avg_max.append(_df_group_avg_max)

# Concatenate the dataframes
df_group_avg_max = pd.concat(list_group_avg_max)

# Concatenate the dataframes and add the polygon data
print("Original length of wspolygon: ", len(wspolygon))
print("Original length of df_group_avg_max: ", len(df_group_avg_max))
df_group_avg_max_polygon = wspolygon.join(
    df_group_avg_max.set_index("gauge_id"), how="right"
).reset_index()
print("Length of df_group_avg_max_polygon: ", len(df_group_avg_max_polygon))
# %%
df_group_avg_max_polygon["process"].unique()
# %%
export_df = (
    df_group_avg_max_polygon[df_group_avg_max_polygon["process"] == "All processes"][
        ["gauge_id", "geometry", "Group_max", "color"]
    ]
    .copy()
    .to_crs(epsg=4326)
)

# %%
# Simplify the geometry
export_df["geometry"] = export_df["geometry"].simplify(tolerance=0.02)


# Sort by area descending
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


export_df = sort_polygons_area_descending(export_df)
# %%
leaflet_json_dir = r"C:\Users\flipl\dev\ry4git.github.io\docs\assets\shp\sig_us"
os.makedirs(leaflet_json_dir, exist_ok=True)

export_df.to_file(
    os.path.join(
        leaflet_json_dir, "shap_most_important_cat_in_map_all_processes.geojson"
    ),
    driver="GeoJSON",
)

# %%
