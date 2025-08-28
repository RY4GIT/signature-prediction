# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np

# %% #########################################################
# Configs
#############################################################

########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
rf_out_dir = os.path.join(
    rf_dir, "output_raraki_20250826_cluster_all"
)  # Random forest output directory (except Wu's)
fig_dir = os.path.join(
    rf_dir, "output_raraki_20250826_figures"
)  # Figure output directory
rf_out_dir_Wu = os.path.join(
    rf_dir, "output_raraki_20250827_cluster_all_Wu"
)  # Wu's random forest output directory
user_name = "raraki"  # User name
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# %% #########################################################
# Plot configs
#############################################################

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

# Attributes info & colors
config_attrs_info_file = "plot_config_attrs_info.csv"
attrs_info = pd.read_csv(config_attrs_info_file)
with open("plot_config_attrs_colors.json", "r") as file:
    attrs_colors = json.load(file)

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
# Signature info
#############################################################

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


# %% #########################################################
# Load Caravan attributes
#############################################################

attrs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv"
attrs = pd.read_csv(attrs_path)
attrs["gauge_id"] = attrs["gauge_id"].astype(str)

attrs.head()

# %% #########################################################
# Load SHAP data
#############################################################

# Load Wu's SHAP data
_df_shap_Wu = pd.read_csv(os.path.join(rf_out_dir_Wu, "shap_values.csv"))
# Load other SHAP data
_df_shap = pd.read_csv(os.path.join(rf_out_dir, "shap_values.csv"))
# Remove Wu's signatures
_df_shap = _df_shap[~_df_shap["sig_name"].isin(sig_Wu_names)]
df_shap = pd.concat([_df_shap, _df_shap_Wu], axis=0)

# Make sure the data is float
df_shap["feature_value"] = df_shap["feature_value"].astype(float)
df_shap["phi"] = df_shap["phi"].astype(float)
df_shap["phi.var"] = df_shap["phi.var"].astype(float)
df_shap = df_shap.merge(
    attrs_info, how="left", left_on="feature", right_on="variable_name"
)
print(len(df_shap))
df_shap.tail()


# %%
# Join df_SHAP with attrs_camels and attrs_hysets on gauge_id
print("Joining SHAP data with attrs_camels and attrs_hysets...")
df_shap = df_shap.merge(attrs, how="left", on="gauge_id")
print(len(df_shap))

# %% #########################################################
# Adjust the cluster column
#############################################################

# Map original cluster labels to broader regions
cluster_to_reclass = {
    1: "Eastern U.S.",
    5: "Eastern U.S.",
    2: "West",
    3: "West",
    4: "West",
    0: "Midwest",
}
df_shap = df_shap.dropna(subset=["cluster"])
grouping_col = "region"
cluster_num = pd.to_numeric(df_shap["cluster"], errors="coerce").astype("Int64")
df_shap[grouping_col] = cluster_num.map(cluster_to_reclass)


# %%
# Get the sum for phi_abs per lopcatino and add it to the dataframe
df_shap["phi_abs"] = df_shap["phi"].abs()
df_shap["phi_abs_sum"] = df_shap.groupby("gauge_id")["phi_abs"].transform("sum")
df_shap["phi_perc"] = df_shap["phi"] / df_shap["phi_abs_sum"] * 100
df_shap["phi_abs_perc"] = df_shap["phi_abs"] / df_shap["phi_abs_sum"] * 100

# %%
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
df_groups = []
for sig in sigs_RF_names_ordered:
    print(sig)
    # _______________________________________________________________________
    # PREPARE THE DATA
    # Get the data for this signature

    # Get the data for this signature
    df_group = (
        df_shap[df_shap["sig_name"] == sig]
        .groupby(["feature", "cluster", "region"])
        .agg(
            median_phi_abs_perc=("phi_abs_perc", "median"),
        )
        .reset_index()
    )
    df_group["sig_name"] = sig
    # _______________________________________________________________________
    # Get the ranking of the feature by phi_abs_perc per cluster
    df_group["rank_median_phi_abs_perc"] = df_group.groupby(["cluster", "region"])[
        "median_phi_abs_perc"
    ].rank(method="first", ascending=False)

    df_groups.append(df_group)

# _______________________________________________________________________
# Get the average contributions from 2 signatures
df_group_all = pd.concat(df_groups)


# %%

# Assign 1 score if the absolute SHAP value is top {top_n} for a given gauge and signature

top_n = 3  # Number of top attributes to assign 1 score
regions = ["Eastern U.S.", "Midwest", "West", "all"]  # Regions to show
clusters = ["all", 0, 1, 2, 3, 4, 5]
cluster_names = [
    "CONUS-wide",
    "Midwest",
    "South",
    "Mountain West",
    "Pacific Northwest",
    "Western Coast and Deserts",
    "Northeast",
]

show_k = 10  # Number of attributes to show in plots

#############################################################

# Rank absolute SHAP within each gauge and signature, then flag top-N
print("Ranking absolute SHAP values...")
# %%
df_group_all["is_top_n"] = (df_group_all["rank_median_phi_abs_perc"] <= top_n).astype(
    int
)

df_group_all = df_group_all.merge(
    attrs_info, how="left", left_on="feature", right_on="variable_name"
)
df_group_all.head()

# %% #########################################################
# COUNT SHAP VALUES PER GAUGE ACROSS SIGNATURES
#############################################################

#############################################
# BY CLUSTER
#############################################
# Clear
# Aggregate counts of top-N occurrences per cluster per signature and attribute
print(f"Counting top-{top_n} SHAP values per cluster...")
grouping_col = "cluster"
df_top_counts_cluster_across_sigs = (
    df_group_all[df_group_all["is_top_n"] == 1]
    .groupby([grouping_col, "feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts_cluster_across_sigs_all = (
    df_group_all[df_group_all["is_top_n"] == 1]
    .groupby(["feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts_cluster_across_sigs_all[grouping_col] = "all"
df_top_counts_cluster_across_sigs = pd.concat(
    [df_top_counts_cluster_across_sigs, df_top_counts_cluster_across_sigs_all],
    ignore_index=True,
)
df_top_counts_cluster_across_sigs.head()


# %%


def plot_counts_by_cluster(
    df_counts: pd.DataFrame,
    clusters: list,
    cluster_names: list,
    top_k_features: int = 15,
    top_n: int = 3,
):
    # Create a figure with subplots
    n_cols = 3
    n_rows = (len(clusters) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(4 * n_cols, 2.8 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    # Plot each signature
    for i, (cluster, cluster_name) in enumerate(zip(clusters, cluster_names)):
        ax = axes[i]

        # Subset the data
        df = df_counts[(df_counts["cluster"] == cluster)].copy()
        if df.empty:
            ax.set_visible(False)
            continue

        # Map colors from Group
        if "color" not in df.columns:
            if "Group" not in df.columns:
                df = df.merge(
                    attrs_info, how="left", left_on="feature", right_on="variable_name"
                )
            df["color"] = df["Group"].map(attrs_colors)

        # Aggregate total counts per feature and group, keep color/group for each feature
        df.sort_values("count", ascending=False, inplace=True)
        features_to_show = list(df.index[:top_k_features])

        # Build plotting frame
        # Select the top features
        df_plot = (
            df.loc[features_to_show]
            .reset_index()
            .rename(columns={"count": "total_count"})
        )

        ax.barh(
            y=df_plot["feature"],
            width=df_plot["total_count"],
            color=df_plot["color"],
            edgecolor="dimgray",
        )
        ax.invert_yaxis()
        ax.set_title(f"{cluster} - {cluster_name}", fontsize=10, loc="left")
        ax.set_xlabel(f"#appearance as top-{top_n}")
        ax.set_ylabel(None)
        ax.tick_params(labelsize=7)

    # Hide any extra axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(
        f"Top {top_n} mean SHAP% count per cluster, across signatures", fontsize=14
    )
    out_grid = f"shap_count_top{top_n}_percphi_all_signatures_by_clusters.{file_type}"
    fig.savefig(os.path.join(fig_dir, out_grid), dpi=300, bbox_inches="tight")
    # plt.close(fig)


plot_counts_by_cluster(
    df_top_counts_cluster_across_sigs.sort_values("count", ascending=False),
    clusters=clusters,
    cluster_names=cluster_names,
    top_k_features=12,
    top_n=top_n,
)

# %%
#############################################
# BY BROADER REGIONS
#############################################

# Aggregate counts of top-N occurrences per region per signature and attribute
print(f"Counting top-{top_n} SHAP values per region...")
grouping_col = "region"
df_top_counts_region_across_sigs = (
    df_group_all[df_group_all["is_top_n"] == 1]
    .groupby([grouping_col, "feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts_region_across_sigs_all = (
    df_group_all[df_group_all["is_top_n"] == 1]
    .groupby(["feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts_region_across_sigs_all[grouping_col] = "all"
df_top_counts_region_across_sigs = pd.concat(
    [df_top_counts_region_across_sigs, df_top_counts_region_across_sigs_all],
    ignore_index=True,
)
df_top_counts_region_across_sigs.head()


# %% #########################################################
# SHOW THE COUNTS IN BAR PLOTS  — ONE SUBPLOT PER SIGNATURE
#############################################################
def plot_counts_by_region(
    df_counts: pd.DataFrame,
    regions: list,
    top_k_features: int = 15,
    top_n: int = 3,
):
    # Create a figure with subplots
    n_cols = 3
    n_rows = (len(clusters) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(4 * n_cols, 2.8 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    # Plot each signature
    for i, region in enumerate(regions):
        ax = axes[i]

        # Subset the data
        df = df_counts[(df_counts["region"] == region)].copy()
        if df.empty:
            ax.set_visible(False)
            continue

        # Map colors from Group
        if "color" not in df.columns:
            if "Group" not in df.columns:
                df = df.merge(
                    attrs_info, how="left", left_on="feature", right_on="variable_name"
                )
            df["color"] = df["Group"].map(attrs_colors)

        # Aggregate total counts per feature and group, keep color/group for each feature
        df.sort_values("count", ascending=False, inplace=True)
        features_to_show = list(df.index[:top_k_features])

        # Build plotting frame
        # Select the top features
        df_plot = (
            df.loc[features_to_show]
            .reset_index()
            .rename(columns={"count": "total_count"})
        )

        ax.barh(
            y=df_plot["feature"],
            width=df_plot["total_count"],
            color=df_plot["color"],
            edgecolor="dimgray",
        )
        ax.invert_yaxis()
        ax.set_title(f"{region}", fontsize=10, loc="left")
        ax.set_xlabel(f"#appearance as top-{top_n}")
        ax.set_ylabel(None)
        ax.tick_params(labelsize=7)

    # Hide any extra axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"Top {top_n} SHAP count, across signatures", fontsize=14)
    out_grid = (
        f"shap_count_top{top_n}_percphi_all_signatures_by_broader_regions.{file_type}"
    )
    fig.savefig(os.path.join(fig_dir, out_grid), dpi=300, bbox_inches="tight")
    # plt.close(fig)


plot_counts_by_region(
    df_top_counts_region_across_sigs,
    regions=regions,
    top_k_features=12,
    top_n=top_n,
)

# %%
