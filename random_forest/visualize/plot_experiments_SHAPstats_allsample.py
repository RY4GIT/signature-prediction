# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import patches
from tqdm import tqdm
import geopandas as gpd

# %%
########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
rf_out_dir = os.path.join(rf_dir, "output_raraki_20250826_cluster_all")
rf_out_dir_Wu = os.path.join(rf_dir, "output_raraki_20250827_cluster_all_Wu")
fig_dir = os.path.join(rf_dir, "output_raraki_20250826_figures")

user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# %%
# ____________________________________________________________________________________
# Plot configs

# Attributes info & colors
config_attrs_info_file = "plot_config_attrs_info.csv"
attrs_info = pd.read_csv(config_attrs_info_file)
with open("plot_config_attrs_colors_high_contrast.json", "r") as file:
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


# %%
######################################################
# R-squares comparison by region
#####################################################

_df_r2_Wu = pd.read_csv(
    os.path.join(rf_out_dir_Wu, "r_squared_all.csv"), index_col="sig_name"
)
_df_r2 = pd.read_csv(
    os.path.join(rf_out_dir, "r_squared_all.csv"), index_col="sig_name"
)
df_rf = pd.concat([_df_r2, _df_r2_Wu], axis=0)

print(len(df_rf))
df_rf.tail()


# %%
# # %%
def plot_r2_conus_wide(dfs_r2):
    # Create bar plot of R2 values for CONUS-wide predictions
    fig, ax = plt.subplots(figsize=(6, 4))
    x_values = dfs_r2["r_squared_cv"]
    x_val_std = dfs_r2["r_squared_cv_std"]

    x_values_orderd = x_values.reindex(sigs_RF_names_ordered)
    x_val_std_orderd = x_val_std.reindex(sigs_RF_names_ordered)
    colors = ["royalblue"] * 4 + ["palegoldenrod"] * 4 + ["lightcoral"] * 6
    ax.bar(
        x_values_orderd.index,
        x_values_orderd.values,
        color=colors,
        alpha=0.8,
        yerr=x_val_std_orderd.values,
        capsize=5,
        error_kw={"ecolor": "dimgrey", "lw": 0.5, "capthick": 1, "capsize": 3},
    )
    ax.set_xlabel(None)
    ax.set_ylabel(r"$R^2$")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"r2_conus_wide.{file_type}"), dpi=300)


plot_r2_conus_wide(df_rf)


# %% ###################################################
# SHAP values
#######################################################


# ##################################################
# SHAP values (bar plots, individual attributes)
########################################################

# Cluster colors
with open("plot_config_expcolors_clusters.json", "r") as file:
    cluster_plot_json = json.load(file)
# Convert keys to integers except for the first item
cluster_info = {int(k) if k.isdigit() else k: v for k, v in cluster_plot_json.items()}
clusters = cluster_info.keys()
print(clusters)


# Function to map colors
def map_colors(group):
    return attrs_colors.get(group, "lightgrey")


# Function to create color dictionary
def create_color_dict(df, var_name):
    df["color"] = df["Group"].apply(map_colors)
    return df.set_index(var_name)["color"].to_dict()


# %% #########################################################
# Load SHAP data
#############################################################

_df_shap_Wu = pd.read_csv(os.path.join(rf_out_dir_Wu, "shap_values.csv"))
_df_shap = pd.read_csv(os.path.join(rf_out_dir, "shap_values.csv"))
_df_shap = _df_shap[~_df_shap["sig_name"].isin(sig_Wu_names)]
df_shap = pd.concat([_df_shap, _df_shap_Wu], axis=0)


# %% Check if the gauge_id overlaps btween _df_r2_Wu and _df_r2
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


# %%
df_shap[df_shap["gauge_id"] == "hysets_07226500"]
# %%

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


# %%
# Function to plot bar plots
def plot_shap(df, cluster_num, cluster_info):
    sigs = sigs_RF_names_ordered
    color_dict = create_color_dict(df, "variable_name")

    n_cols = 5
    n_rows = (len(sigs) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(8 * n_cols, 10 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    for i, sig in enumerate(sigs):
        sig_data = df[df["sig_name"] == sig]

        # Get the mean absolute SHAP value for each attribute
        sig_data["phi_abs"] = sig_data["phi"].abs()
        sig_data = (
            sig_data.groupby("feature")["phi_abs"].mean().sort_values(ascending=False)
        )

        df_subset = sig_data.reset_index()

        sns.barplot(
            data=df_subset,
            x="phi_abs",
            y="feature",
            palette=color_dict,
            ax=axes[i],
        )
        axes[i].set_title(sig, loc="left", fontsize=30)
        axes[i].set_xlabel(r"$\overline{|\phi|}$")
        axes[i].set_ylabel(None)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(cluster_name, fontsize=24)
    fig.subplots_adjust(top=0.9)
    fig.savefig(
        os.path.join(fig_dir, f"shap_bar_{cluster_num}.{file_type}"),
        dpi=1200,
    )


# #####################################################
# SHAP values (bar plots, individual attributes)
# #####################################################

for cluster_num in ["all", 0, 1, 2, 3, 4, 5]:
    print(f"Processing {cluster_num}...")

    plot_shap(df_shap, cluster_num=cluster_num, cluster_info=cluster_info)


# %%
# Function to plot bar plots by category
def plot_shap_by_category(df, cluster_num, cluster_info):
    # sigs = df["sig_name"].unique()
    sigs = sigs_RF_names_ordered  # When you want to subset the signatures

    n_cols = 5
    n_rows = (len(sigs) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(4 * n_cols, 3 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    for i, sig in enumerate(sigs):
        # Get data for this signature
        df_sig = df[df["sig_name"] == sig].copy()

        # Group by Group (category) and calculate mean phi
        df_sig["phi_abs"] = df_sig["phi"].abs()
        df_grouped = df_sig.groupby("Group")["phi_abs"].mean().reset_index()

        # Sort by mean importance
        df_grouped = df_grouped.sort_values(by="phi_abs", ascending=False)

        # Create color dictionary for groups
        colors = [attrs_colors.get(group, "lightgrey") for group in df_grouped["Group"]]

        # Plot
        sns.barplot(
            data=df_grouped,
            x="phi_abs",
            y="Group",
            palette=dict(zip(df_grouped["Group"], colors)),
            ax=axes[i],
        )
        axes[i].set_title(sig, loc="left")
        # axes[i].set_ylabel(None)
        axes[i].set_xlabel(r"$\overline{|\phi|}$")

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"SHAP Importance by Category: {cluster_num}", fontsize=24)
    # fig.subplots_adjust(top=0.9)

    fig.savefig(
        os.path.join(fig_dir, f"shap_cat_{cluster_num}.{file_type}"),
        dpi=1200,
    )


# #####################################################
# Shapley (bar plots, by category)
# #####################################################
plot_shap_by_category(df_shap, cluster_num="all", cluster_info=cluster_info)

# %% ###################################################
# PLOT SHAP IN A MAP
########################################################


def plot_shap_in_map(df, sig_name, var_name):
    attr_names = df["variable_name"].unique()

    n_cols = 2
    n_rows = (len(attr_names) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(10 * n_cols, 5 * n_rows),
        constrained_layout=True,
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    axes = axes.flatten()

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="darkgrey",  # Set land color to light gray
    )

    water = cfeature.NaturalEarthFeature(
        "physical",
        "lakes",
        "50m",
        edgecolor="face",
        facecolor="white",  # Set water color to light blue
    )

    for i, attr_name in enumerate(attr_names):
        # Get data for this signature
        df_sig = df[df["sig_name"] == sig_name].copy()

        ax = axes[i]
        ax.add_feature(land)
        ax.add_feature(water)

        # Plot scatter
        df_sig_feature = df_sig[df_sig["feature"] == attr_name]

        # Limit the vmin and vmax based on the quantiles of the data
        if df_sig_feature[var_name].empty:
            continue

        # Limit the vmin and vmax based on the quantiles of the data
        vmin, vmax = np.quantile(df_sig_feature[var_name], [0.20, 0.80])

        scatter_obj = ax.scatter(
            df_sig_feature["gauge_lon"],
            df_sig_feature["gauge_lat"],
            c=df_sig_feature[var_name],
            alpha=0.5,
            s=9,
            zorder=99,
            vmin=vmin,
            vmax=vmax,
        )
        cbar = plt.colorbar(scatter_obj, ax=ax, shrink=0.3)
        if var_name == "phi":
            cbar.set_label(r"$\phi$")
        elif var_name == "phi_abs":
            cbar.set_label(r"$|\phi|$")
        elif var_name == "phi_perc":
            cbar.set_label(r"$\phi/\sum|\phi|$ (%)")
        elif var_name == "phi_abs_perc":
            cbar.set_label(r"$|\phi|/\sum|\phi|$ (%)")
        ax.set_title(attr_name)

    fig.suptitle(sig_name, fontsize=24)

    # Save plot
    if var_name == "phi":
        file_name = f"shap_in_map_{sig_name}.{file_type}"
    elif var_name == "phi_abs":
        file_name = f"shap_abs_in_map_{sig_name}.{file_type}"
    elif var_name == "phi_perc":
        file_name = f"shap_perc_in_map_{sig_name}.{file_type}"
    elif var_name == "phi_abs_perc":
        file_name = f"shap_abs_perc_in_map_{sig_name}.{file_type}"

    fig.savefig(
        os.path.join(fig_dir, file_name),
        dpi=300,
        bbox_inches="tight",
    )

    # Clear the figure
    plt.close(fig)


# %%
# ###################################################
# SHAP % PER SIGNATURE PER ATTRIBUTE IN A MAP
#####################################################
# Plot the relative contribution of each attribute to the signature
for sig_name in tqdm(sigs_RF_names_ordered[:-3], desc="Processing SHAP in map"):
    plot_shap_in_map(df_shap_with_attrs, sig_name, "phi_perc")


# %% Sometimes the loop runs out of memory, here to redo it manually
for sig_name in ["SE_thresh_signif", "R_Pint_RC", "R_Pvol_RC"]:
    print(f"Processing {sig_name}...")
    plot_shap_in_map(df_shap_with_attrs, sig_name, "phi_perc")


# %% ###################################################
# PLOT SHAP VS ATTRIBUTE SCATTER PLOT
#######################################################
def plot_shap_vs_attr(df, sig_name, cluster_num, cluster_info):
    attr_names = df["variable_name"].unique()

    n_cols = 5
    n_rows = (len(attr_names) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(4 * n_cols, 3 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    for i, attr_name in enumerate(attr_names):
        # Get data for this signature
        df_sig = df[df["sig_name"] == sig_name].copy()

        ax = axes[i]

        # Plot scatter
        df_sig_feature = df_sig[df_sig["feature"] == attr_name]
        # df_sig_feature_filt = df_sig_feature[df_sig_feature["cluster"] == cluster_num]
        ax.scatter(
            df_sig_feature["feature_value"],
            df_sig_feature["phi"],
            alpha=0.5,
            s=9,
        )

        # Add labels and title
        ax.set_xlabel(attr_name)
        ax.set_ylabel(r"$\phi$")

        # Add zero line
        ax.axhline(y=0, color="k", linestyle="--", alpha=0.3)

    cluster_name = f"{sig_name} {cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(cluster_name, fontsize=24)

    # Save plot
    fig.savefig(
        os.path.join(
            fig_dir, f"shap_vs_attr_{sig_name}_cluster_{cluster_num}.{file_type}"
        ),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


# %%
# #####################################################
# PLOT SHAP VS ATTRIBUTE (partial dependence plot like figure)
########################################################

for sig_name in sigs_RF_names_ordered:
    print(f"Processing {sig_name}...")
    plot_shap_vs_attr(df_shap_with_attrs, sig_name, "all", cluster_info)

# %%
for sig_name in ["R_Pint_RC", "R_Pvol_RC"]:
    print(f"Processing {sig_name}...")
    plot_shap_vs_attr(df_shap_with_attrs, sig_name, "all", cluster_info)


# %% ###################################################
# Plot the mean phi_abs_perc per category in a map
########################################################
def plot_shap_in_map_by_group(df, sig_name):
    group_names = df["Group"].unique()
    n_cols = 2
    n_rows = (len(group_names) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(8 * n_cols, 4 * n_rows),
        constrained_layout=True,
        subplot_kw={"projection": ccrs.PlateCarree()},
    )
    axes = axes.flatten()

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="darkgrey",  # Set land color to light gray
    )

    water = cfeature.NaturalEarthFeature(
        "physical",
        "lakes",
        "50m",
        edgecolor="face",
        facecolor="white",  # Set water color to light blue
    )

    for i, group_name in enumerate(group_names):
        # Get data for this signature
        df_group = df[df["Group"] == group_name].copy()

        ax = axes[i]
        ax.add_feature(land)
        ax.add_feature(water)

        # Limit the vmin and vmax based on the quantiles of the data
        if df_group["mean_phi_abs_perc"].empty:
            continue

        # Limit the vmin and vmax based on the quantiles of the data
        vmin, vmax = np.quantile(df_group["mean_phi_abs_perc"], [0.20, 0.80])

        scatter_obj = ax.scatter(
            df_group["gauge_lon"],
            df_group["gauge_lat"],
            c=df_group["mean_phi_abs_perc"],
            alpha=0.5,
            s=9,
            zorder=99,
            vmin=vmin,
            vmax=vmax,
        )
        cbar = plt.colorbar(scatter_obj, ax=ax, shrink=0.3)
        cbar.set_label(r"$\overline{|\phi|/\sum|\phi|}$ (%)")
        ax.set_title(group_name)

    fig.suptitle(sig_name, fontsize=24)

    # Save plot
    file_name = f"shap_perc_cat_in_map_{sig_name}.{file_type}"

    fig.savefig(
        os.path.join(fig_dir, file_name),
        dpi=300,
        bbox_inches="tight",
    )

    # Clear the figure
    plt.close(fig)


# %% #####################################################
# Plot the max category per location
########################################################


def plot_shap_in_map_max(df_group_max, sig_name, varname="max_mean_phi_abs_perc"):
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add the BORDERS feature first
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

    # Add the land feature with edgecolor set to black
    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
    )
    water = cfeature.NaturalEarthFeature(
        "physical",
        "lakes",
        "50m",
        edgecolor="face",
    )
    ax.add_feature(
        land,
        facecolor="dimgrey",  # Keep facecolor as desired
        edgecolor="black",  # Set edgecolor to black
        linewidth=0.5,  # Optionally adjust linewidth for edges
    )
    ax.add_feature(water, facecolor="white", edgecolor="black", linewidth=0.5)

    # Add state boundary lines beneath data
    ax.add_feature(
        cfeature.STATES,
        edgecolor="#9e9e9e",
        linewidth=0.4,
        zorder=10,
    )

    # Plot the max category per location
    max_opacity = df_group_max[varname].quantile(0.90)
    ax.scatter(
        df_group_max["gauge_lon"],
        df_group_max["gauge_lat"],
        c=df_group_max["color"],
        alpha=np.clip(
            df_group_max[varname] / max_opacity, 0, 1
        ),  # Scale alpha by mean_phi_abs_perc percentage
        s=10,
        zorder=99,
    )
    ax.set_title(sig_name)

    # Add a legend
    legend_elements = [
        patches.Patch(
            facecolor=attrs_colors[group],
            edgecolor="black",
            label=f"{group} ({df_group_max.groupby('Group_max').count()['gauge_id'].get(group, 0):d})",
        )
        for group in attrs_colors.keys()
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    # Save plot
    file_name = f"shap_most_important_cat_in_map_{sig_name}.{file_type}"

    # Set extent to CONUS
    conus_extent = [-125.5, -66.95, 24.396308, 47.5]
    ax.set_extent(conus_extent)

    # Set spines invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Display the map
    plt.tight_layout()
    fig.savefig(
        os.path.join(fig_dir, file_name),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


# %% #####################################################
# Calculate the percentage of SHAP for each attribute
########################################################
# Data preparation

for sig_name in sigs_RF_names_ordered:
    print(f"Processing {sig_name} ...")

    # _______________________________________________________________________
    # PREPARE THE DATA
    # Get the data for this signature
    df_shap_sig = df_shap_with_attrs[df_shap_with_attrs["sig_name"] == sig_name].copy()

    # _______________________________________________________________________
    # Get mean phi_abs_perc per category and create a grouped dataframe
    df_group = (
        df_shap_sig.groupby(["Group", "gauge_id"])
        .agg(
            mean_phi_abs_perc=("phi_abs_perc", "mean"),
            gauge_lon=("gauge_lon", "first"),
            gauge_lat=("gauge_lat", "first"),
        )
        .reset_index()
    )

    # _______________________________________________________________________
    # Plot the relative contribution of each attribute to the signature
    plot_shap_in_map_by_group(df_group, sig_name)

    # _______________________________________________________________________
    # PREPARE THE DATA
    # For each gauge_id, get the row with the maximum phi_abs_perc
    df_group_max = (
        df_group.loc[df_group.groupby("gauge_id")["mean_phi_abs_perc"].idxmax()][
            ["gauge_id", "mean_phi_abs_perc", "Group", "gauge_lon", "gauge_lat"]
        ]
        .rename(
            columns={
                "mean_phi_abs_perc": "max_mean_phi_abs_perc",
                "Group": "Group_max",
            }
        )
        .reset_index(drop=True)
    )

    df_group_max["color"] = df_group_max["Group_max"].map(attrs_colors)
    print(df_group_max["Group_max"].value_counts())
    print("--------------------------------")

    # _______________________________________________________________________
    # Plot the max category per location
    plot_shap_in_map_max(df_group_max, sig_name, varname="max_mean_phi_abs_perc")


# %% ###############################################################
# Get the average contributions from 2 signatures and plot the max category per location
########################################################
sig_pairs = {
    # 0: {"Process": "Baseflow", "sigs": ["BFI", "BaseflowRecessionK"]},
    # 1: {
    #     "Process": "High storage capacity",
    #     "sigs": ["AverageStorage", "RecessionParameters_b"],
    # },
    # 2: {"Process": "Water balance losses", "sigs": ["EventRR", "TotalRR"]},
    # 3: {
    #     "Process": "Seasonal variability",
    #     "sigs": ["Recession_a_Seasonality", "VariabilityIndex"],
    # },
    # 4: {
    #     "Process": "Overland flow",
    #     "sigs": ["IE_thresh", "IE_thresh_signif", "SE_thresh", "SE_thresh_signif"],
    # },
    # 5: {
    #     "Process": "Overland flow threshold",
    #     "sigs": ["IE_thresh", "SE_thresh"],
    # },
    # 6: {
    #     "Process": "Overland flow significance",
    #     "sigs": ["IE_thresh_signif", "SE_thresh_signif"],
    # },
    # 7: {
    #     "Process": "Overland flow (IE vs. SE)",
    #     "sigs": ["R_Pint_RC", "R_Pvol_RC"],
    # },
    8: {
        "Process": "All processes",
        "sigs": sigs_RF_names_ordered,
    },
}
# %%
for pair in sig_pairs.values():
    print(pair["Process"])
    print(pair["sigs"])
    print("--------------------------------")
    # _______________________________________________________________________
    # PREPARE THE DATA
    # Get the data for this signature
    df_groups = []
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

        df_groups.append(df_group)

    # _______________________________________________________________________
    # Get the average contributions from 2 signatures
    df_group_all = pd.concat(df_groups)

    if pair["Process"] == "All processes":
        stat = "median"
    else:
        stat = "mean"
    # Recalculate mean after adding sig_name
    df_group_avg = (
        df_group_all.groupby(["gauge_id", "Group"])
        .agg(
            mean_phi_abs_perc=("mean_phi_abs_perc", stat),
            gauge_lon=("gauge_lon", "first"),
            gauge_lat=("gauge_lat", "first"),
            count=("mean_phi_abs_perc", "count"),
        )
        .reset_index()
    ).rename(columns={"mean_phi_abs_perc": f"{stat}_phi_abs_perc_sigs"})

    # For each gauge_id, get the row with the maximum phi_abs_perc
    df_group_avg_max = (
        df_group_avg.loc[
            df_group_avg.groupby("gauge_id")[f"{stat}_phi_abs_perc_sigs"].idxmax()
        ][
            [
                "gauge_id",
                f"{stat}_phi_abs_perc_sigs",
                "Group",
                "gauge_lon",
                "gauge_lat",
                "count",
            ]
        ]
        .rename(
            columns={
                f"{stat}_phi_abs_perc_sigs": f"max_{stat}_phi_abs_perc",
                "Group": "Group_max",
            }
        )
        .reset_index(drop=True)
    )

    df_group_avg_max["color"] = df_group_avg_max["Group_max"].map(attrs_colors)
    print(df_group_avg_max["Group_max"].value_counts())

    print("--------------------------------")

    # _______________________________________________________________________
    # Plot the max category per location
    # Use the process name as sig_name for plotting
    process_name = pair["Process"]
    plot_shap_in_map_max(
        df_group_avg_max, process_name, varname=f"max_{stat}_phi_abs_perc"
    )


print(len(wspolygon))
print(len(df_group_avg_max))
df_group_avg_max_polygon = wspolygon.join(
    df_group_avg_max.set_index("gauge_id"), how="right"
)
print(len(df_group_avg_max_polygon))


# %%
gauge_id_less_sigs = df_group_avg_max_polygon[df_group_avg_max_polygon["count"] < 3]
gauge_id_less_sigs

# %% ##################################
# The key figure (without cities)
#######################################
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


df_group_avg_max_polygon["area"] = df_group_avg_max_polygon["geometry"].area
df_group_avg_max_polygon.sort_values(by="area", ascending=False, inplace=True)

# Plot the max category per location
df_group_avg_max_polygon.dropna(subset=["max_median_phi_abs_perc"], inplace=True)
max_opacity = df_group_avg_max_polygon["max_median_phi_abs_perc"].quantile(0.75)


polygon_obj = df_group_avg_max_polygon.plot(
    ax=ax,
    color=df_group_avg_max_polygon["color"],
    alpha=np.clip(
        df_group_avg_max_polygon["max_median_phi_abs_perc"] / max_opacity, 0, 1
    ),  # Scale alpha by mean_phi_abs_perc percentage
    zorder=99,
)
# ax.set_title(sig_name)

# Add a legend
legend_elements = [
    patches.Patch(
        facecolor=attrs_colors[group],
        edgecolor="black",
        label=f"{group} ({df_group_avg_max_polygon.groupby('Group_max').count()['geometry'].get(group, 0):d})",
    )
    for group in attrs_colors.keys()
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=11)

# Save plot
file_name = f"shap_most_important_cat_in_map_all_processes_median.{file_type}"

# Set extent to CONUS
ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
# ax.set_extent(conus_extent)

# Set spines invisible
for spine in ax.spines.values():
    spine.set_visible(False)

# Display the map
plt.tight_layout()
fig.savefig(
    os.path.join(fig_dir, file_name),
    dpi=300,
    bbox_inches="tight",
)


# %%
# %% ##################################
# The key figure (with cities)
#######################################
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


######### Add major cities (dots and labels) #########
# Define a list of major cities within the CONUS

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
    # {"name": "Minneapolis", "lon": -93.2650, "lat": 44.9778},
    {"name": "Las Vegas", "lon": -115.1398, "lat": 36.1699},
    {"name": "Portland", "lon": -122.6765, "lat": 45.5152},
    # Requested additions
    {"name": "Cleveland", "lon": -81.6944, "lat": 41.4993},
    {"name": "Knoxville", "lon": -83.9207, "lat": 35.9606},
    {"name": "Nashville", "lon": -86.7816, "lat": 36.1627},
    {"name": "Benton", "lon": -92.5868, "lat": 34.5645},  # AR
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

df_group_avg_max_polygon["area"] = df_group_avg_max_polygon["geometry"].area
df_group_avg_max_polygon.sort_values(by="area", ascending=False, inplace=True)

# Plot the max category per location
df_group_avg_max_polygon.dropna(subset=["max_median_phi_abs_perc"], inplace=True)
max_opacity = df_group_avg_max_polygon["max_median_phi_abs_perc"].quantile(0.75)

df_plot = df_group_avg_max_polygon[df_group_avg_max_polygon["count"] > 3]
polygon_obj = df_plot.plot(
    ax=ax,
    color=df_group_avg_max_polygon["color"],
    alpha=np.clip(
        df_group_avg_max_polygon["max_median_phi_abs_perc"] / max_opacity, 0, 1
    ),  # Scale alpha by mean_phi_abs_perc percentage
    zorder=99,
)
# ax.set_title(sig_name)

# Add a legend
legend_elements = [
    patches.Patch(
        facecolor=attrs_colors[group],
        edgecolor="black",
        label=f"{group} ({df_group_avg_max_polygon.groupby('Group_max').count()['geometry'].get(group, 0):d})",
    )
    for group in attrs_colors.keys()
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=11)

# Save plot
file_name = (
    f"shap_most_important_cat_in_map_all_processes_median_with_cities.{file_type}"
)

# Set extent to CONUS
ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
# ax.set_extent(conus_extent)

# Set spines invisible
for spine in ax.spines.values():
    spine.set_visible(False)

# Display the map
plt.tight_layout()
fig.savefig(
    os.path.join(fig_dir, file_name),
    dpi=300,
    bbox_inches="tight",
)

# %% ###############################################################
# Investigate the New Mexico outlier
####################################################################

# Get the row with the Group_max being "Topography" where the gauge_lon and gauge_lat are within the New Mexico
gauge_id_interest = df_group_avg_max_polygon[
    (df_group_avg_max_polygon["Group_max"] == "Human alteration")
    & (df_group_avg_max_polygon["gauge_lon"] > -109.203680)
    & (df_group_avg_max_polygon["gauge_lon"] < -102.986323)
    & (df_group_avg_max_polygon["gauge_lat"] > 31.166394)
    & (df_group_avg_max_polygon["gauge_lat"] < 37.128153)
].index
print(gauge_id_interest)
# %% Get the mean phi_abs_perc for the gauge_id_interest
# df_shap_with_attrs.merge(attrs_info, on="variable_name", how="left")

# %%
df_gauges_of_interest = df_shap_with_attrs[
    df_shap_with_attrs["gauge_id"].isin(gauge_id_interest)
].sort_values(by="phi_perc", ascending=False)
df_gauges_of_interest.head()


# %%
check_dir = "G:/Shared drives/Signatures -- large scale/baseflow/RAraki/out/rf/output_raraki_20250826_figures/check_results"
os.makedirs(check_dir, exist_ok=True)
for gauge_id in gauge_id_interest:
    for sig_name in sigs_RF_names_ordered:
        df_plot = (
            df_shap_with_attrs[df_shap_with_attrs["gauge_id"] == gauge_id]
            .loc[df_shap_with_attrs["sig_name"] == sig_name]
            .sort_values(by="phi_perc", ascending=False)
        )

        if len(df_plot) > 0:  # Only plot if there is data
            plt.figure(figsize=(10, 6))

            # Create the bar plot manually instead of using df.plot()
            y_pos = np.arange(len(df_plot))
            colors = [attrs_colors.get(group, "gray") for group in df_plot["Group"]]

            plt.barh(y_pos, df_plot["phi_perc"], color=colors)
            plt.yticks(y_pos, df_plot["variable_name"])
            plt.title(f"Gauge ID: {gauge_id}, Signature: {sig_name}")
            plt.xlabel("SHAP Value Percentage")

            plt.tight_layout()
            plt.savefig(os.path.join(check_dir, f"{gauge_id}_{sig_name}.png"))
            plt.close()

# %%
df_shap_with_attrs["color"] = df_shap_with_attrs["Group"].map(attrs_colors)
df_shap_with_attrs
# %%

df_group_avg_max_polygon[df_group_avg_max_polygon["gauge_id"].isin(gauge_id_interest)]

# %%
sigs_RF_names_ordered
# %%
df_shap_with_attrs
# %%
df_group_avg_max_polygon
# %%
# df_group_avg
# # %%
# df_shap_with_attrs[df_shap_with_attrs["gauge_id"] == "camels_01013500"]
df_group_avg_max_polygon
# %%
