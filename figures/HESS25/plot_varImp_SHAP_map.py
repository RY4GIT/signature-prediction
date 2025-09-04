# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import patches
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

df_group_avg_max_polygon["process"].unique()


# %% for each process, plot the max category per location
for process in process_list:
    print("--------------------------------")
    df_group_avg_max_process = df_group_avg_max_polygon[
        df_group_avg_max_polygon["process"] == process
    ]
    print(process)
    print(df_group_avg_max_polygon["Group_max"].value_counts())


# %% ##################################
# The key figure (without cities)
#######################################
def plot_shap_in_map_max(
    df,
    process,
    varname="max_median_phi_abs_perc",
    file_type="png",
    show_cities=False,
):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add the BORDERS feature first
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

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
        facecolor="#c3c4c8",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=1.0,  # Optionally adjust linewidth for edges
    )

    # Add state boundary lines beneath data
    ax.add_feature(
        cfeature.STATES,
        edgecolor="#9e9e9e",
        linewidth=0.75,
    )

    if show_cities:
        major_cities = [
            {"name": "New York", "lon": -74.0060, "lat": 40.7128},
            {"name": "Los Angeles", "lon": -118.2437, "lat": 34.0522},
            {"name": "Chicago", "lon": -87.6298, "lat": 41.8781},
            {"name": "Houston", "lon": -95.3698, "lat": 29.7604},
            {"name": "Phoenix", "lon": -112.0740, "lat": 33.4484},
            {"name": "Philadelphia", "lon": -75.1652, "lat": 39.9526},
            {"name": "San Antonio", "lon": -98.4936, "lat": 29.4241},
            {"name": "San Diego", "lon": -117.1611, "lat": 32.7157},
            {"name": "Dallas", "lon": -96.7970, "lat": 32.7767},
            {"name": "San Jose", "lon": -121.8863, "lat": 37.3382},
            {"name": "Austin", "lon": -97.7431, "lat": 30.2672},
            {"name": "Jacksonville", "lon": -81.6557, "lat": 30.3322},
            {"name": "San Francisco", "lon": -122.4194, "lat": 37.7749},
            {"name": "Seattle", "lon": -122.3321, "lat": 47.6062},
            {"name": "Denver", "lon": -104.9903, "lat": 39.7392},
            {"name": "Miami", "lon": -80.1918, "lat": 25.7617},
            {"name": "Boston", "lon": -71.0589, "lat": 42.3601},
            {"name": "Atlanta", "lon": -84.3880, "lat": 33.7490},
            {"name": "Washington, DC", "lon": -77.0369, "lat": 38.9072},
            {"name": "Detroit", "lon": -83.0458, "lat": 42.3314},
            {"name": "Minneapolis", "lon": -93.2650, "lat": 44.9778},
            {"name": "Las Vegas", "lon": -115.1398, "lat": 36.1699},
            {"name": "Portland", "lon": -122.6765, "lat": 45.5152},
            {"name": "Seattle", "lon": -122.3321, "lat": 47.6062},
            {"name": "Indianapolis", "lon": -86.1581, "lat": 39.7684},
            {"name": "Cleveland", "lon": -81.6944, "lat": 41.4993},
            {"name": "Knoxville", "lon": -83.9207, "lat": 35.9606},
            {"name": "Nashville", "lon": -86.7816, "lat": 36.1627},
            {"name": "Benton", "lon": -92.5868, "lat": 34.5645},
            {"name": "Memphis", "lon": -90.0490, "lat": 35.1495},
            {"name": "Birmingham", "lon": -86.8104, "lat": 33.5186},
            {"name": "Charlotte", "lon": -80.8431, "lat": 35.2271},
            {"name": "St. Louis", "lon": -90.1994, "lat": 38.6270},
            {"name": "Raleigh", "lon": -78.6382, "lat": 35.7796},
            {"name": "Cincinnati", "lon": -84.5120, "lat": 39.1031},
            {"name": "Pierre", "lon": -100.3510, "lat": 44.3683},
            {"name": "Omaha", "lon": -95.9970, "lat": 41.2524},
            {"name": "Kansas City", "lon": -94.5786, "lat": 39.0997},
            {"name": "Oklahoma City", "lon": -97.5164, "lat": 35.4676},
            {"name": "Santa Fe", "lon": -105.9378, "lat": 35.6870},
        ]

        # Plot city markers
        for city in major_cities:
            ax.scatter(
                city["lon"],
                city["lat"],
                c="k",
                s=18,
                edgecolors="white",
                linewidths=0.5,
                zorder=300,
                transform=ccrs.PlateCarree(),
            )
            import matplotlib.patheffects as pe

            ax.text(
                city["lon"] + 0.3,
                city["lat"] + 0.15,
                city["name"],
                fontsize=8,
                color="k",
                zorder=301,
                transform=ccrs.PlateCarree(),
                ha="left",
                va="bottom",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

    df["area"] = df["geometry"].area
    df.sort_values(by="area", ascending=False, inplace=True)

    # Plot the max category per location
    df.dropna(subset=[varname], inplace=True)
    max_opacity = df[varname].quantile(0.80)

    if varname == "count":
        df.plot(ax=ax, column=varname, legend=True, zorder=99)
    else:
        # Filter out regions with less than 8 signatures considered
        # (8 baseflow & water loss signatures, and 4 overland flow signatures are the default)
        if process == "All processes":
            df_filt = df[df["count"] >= 8]
        else:
            df_filt = df.copy()

        df_filt.plot(
            ax=ax,
            column=varname,
            color=df_filt["color"],
            legend=True,
            alpha=np.clip(
                df_filt[varname] / max_opacity, 0, 1
            ),  # Scale alpha by mean_phi_abs_perc percentage
            zorder=99,
        )

    if varname != "count":
        # Add a legend
        legend_elements = [
            patches.Patch(
                facecolor=attrs_colors[group],
                edgecolor="black",
                label=f"{group} ({df.groupby('Group_max').count()['geometry'].get(group, 0):d})",
            )
            for group in attrs_colors.keys()
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=11)

    # Save plot
    if not show_cities:
        file_name = f"shap_most_important_cat_in_map_{process}_{varname}.{file_type}"
    else:
        file_name = f"shap_most_important_cat_in_map_{process}_{varname}_with_cities.{file_type}"

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    # ax.set_extent(conus_extent)

    # Set spines invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Display the map
    # Output directory

    if process == "All processes":
        fig_out_dir = fig_dir
    else:
        fig_out_dir = sfig_dir

    plt.tight_layout()
    fig.savefig(
        os.path.join(fig_out_dir, file_name),
        dpi=300,
        bbox_inches="tight",
    )


# %% ######################################################
# Plot the "All processes" etc. figures
########################################################
for process in df_group_avg_max_polygon["process"].unique():
    df_group_avg_max_process = df_group_avg_max_polygon[
        df_group_avg_max_polygon["process"] == process
    ].copy()

    if process == "All processes":
        # This includes 14 signatures, so the median is more robust
        stats = "median"
    else:
        # This includes around 2 signatures, so the mean is more robust
        stats = "mean"

    plot_shap_in_map_max(
        df_group_avg_max_process,
        process=process,
        varname=f"max_{stats}_phi_abs_perc",
        file_type="png",
        show_cities=False,
    )
