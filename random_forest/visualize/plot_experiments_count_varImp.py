# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np

# %%
########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
output_date = "20250826"
output_date_Wu = "20250827"
user_name = "raraki"
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

fig_dir = os.path.join(rf_dir, f"output_{user_name}_{output_date}_figures")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


# ____________________________________________________________________________________
# Plot configs

# Attributes info & colors
config_attrs_info_file = "plot_config_attrs_info.csv"
attrs_info = pd.read_csv(config_attrs_info_file)
with open("plot_config_attrs_colors_high_contrast.json", "r") as file:
    attrs_colors = json.load(file)

# Signature info
cofig_sigs_file = (
    r"C:\Users\flipl\dev\signature-prediction\signatures\visualize\plot_sigs_config.csv"
)
sigs_info = pd.read_csv(cofig_sigs_file)
sig_names = sigs_info["column_name"]
derived_sig_names = [
    "avg_IE_SE_thresh",
    "avg_IE_SE_signif",
    "diff_RCPint_RCPvol",
]
sigs_RF_names = np.setdiff1d(sig_names, derived_sig_names)
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


# %% # ____________________________________________________________________________________
# Some base data loaders


# Function to load data
def load_incMSE_by_cluster(
    rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
):
    file_path = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date}_cluster_{cluster_num}",
        "var_importance.csv",
    )
    file_path_Wu = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date_Wu}_cluster_{cluster_num}_Wu",
        "var_importance.csv",
    )

    _df_imp = pd.read_csv(file_path)
    _df_imp_Wu = pd.read_csv(file_path_Wu)

    df_imp = pd.concat([_df_imp, _df_imp_Wu], axis=0)

    df_imp = df_imp.merge(
        attrs_info, how="left", left_on="predictor", right_on="variable_name"
    )

    return df_imp


df_imp = []
for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    _df_imp = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
    )
    _df_imp["cluster"] = cluster_num
    df_imp.append(_df_imp)
df_imp = pd.concat(df_imp, axis=0)
df_imp.head()

# %%
# Add some broader regions
# Map original cluster labels to broader regions
cluster_to_reclass = {
    1: "Eastern U.S.",
    5: "Eastern U.S.",
    2: "West",
    3: "West",
    4: "West",
    0: "Midwest",
}
df_imp = df_imp.dropna(subset=["cluster"])
grouping_col = "region"
cluster_num = pd.to_numeric(df_imp["cluster"], errors="coerce").astype("Int64")
df_imp[grouping_col] = cluster_num.map(cluster_to_reclass)
df_imp.tail()

# %% ################################################
# Count top attributes by incMSE
#####################################################

# %% #########################################################
# COUNT SHAP VALUES PER GAUGE
#############################################################

# %% #########################################################
# COUNT SHAP VALUES PER GAUGE
#############################################################

########################CHANGE HERE#####################

# Assign 1 score if the absolute SHAP value is top {top_n} for a given gauge and signature

top_n = 3  # Number of top attributes to assign 1 score
show_k = 10  # Number of attributes to show in plots
regions = ["Eastern U.S.", "Midwest", "West", "all"]  # Regions to show
cluster_dict = {
    3: "Pacific Northwest",
    0: "Midwest",
    5: "Northeast",
    4: "Western Coast and Deserts",
    2: "Mountain West",
    1: "South",
}
clusters = ["all", *cluster_dict.keys()]
cluster_names = ["CONUS-wide", *cluster_dict.values()]


#############################################################


#############################################################
# BY CLUSTER
#############################################################
# Rank absolute SHAP within each gauge and signature, then flag top-N
print("Ranking absolute SHAP values...")
# Rank %IncMSE within each predictor, signature and cluster group
df_imp["rank_by_cluster"] = df_imp.groupby(["sig_name", "cluster"])["%IncMSE"].rank(
    method="first", ascending=False
)

# Flag top-N
df_imp["is_top_n"] = (df_imp["rank_by_cluster"] <= top_n).astype(int)
df_imp.head()
# %% #########################################################
# Count the score per cluster
#############################################################

# Aggregate counts of top-N occurrences per cluster per attribute, across signatures
print(f"Counting top-{top_n} SHAP values per cluster...")
grouping_col = "cluster"
df_top_counts = (
    df_imp[df_imp["is_top_n"] == 1]
    .groupby([grouping_col, "predictor"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts.head()

# %% #########################################################
# Show and save the table for the top 10 SHAP values per region
#############################################################

print(f"Showing and saving the table for the top {show_k} incMSE values per cluster...")
for cluster, cluster_name in zip(clusters, cluster_names):
    print(f"{cluster} - {cluster_name} — top {top_n} attributes by incMSE-count:")
    # Subset the data
    dfc = df_top_counts[df_top_counts["cluster"] == cluster].sort_values(
        "count", ascending=False
    )
    top_attrs = dfc.head(show_k)
    # print(f"{cluster} - {cluster_name} — top {top_n} attributes by incMSE-count:")
    if top_attrs.empty:
        print("  (no data)")
    else:
        print(top_attrs[["predictor", "count"]].to_string(index=False))
    print("--------------------------------")

# Out put them as csv file
df_top_counts.to_csv(
    os.path.join(fig_dir, f"top{top_n}_attrs_by_incMSE_count_cluster.csv"), index=False
)


# %% #########################################################
# SHOW THE COUNTS IN BAR PLOTS  — ONE SUBPLOT PER SIGNATURE
#############################################################
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
        figsize=(4 * n_cols, 3.2 * n_rows),
        constrained_layout=True,
    )
    # increase font size
    plt.rcParams.update({"font.size": 12})
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
            df = df.merge(
                attrs_info, how="left", left_on="predictor", right_on="variable_name"
            )
            df["color"] = df["Group"].map(attrs_colors)

        # Aggregate total counts per feature and group, keep color/group for each feature
        df.sort_values("count", ascending=False, inplace=True)
        predictors_to_show = list(df.index[:top_k_features])

        # Build plotting frame
        # Select the top features
        df_plot = (
            df.loc[predictors_to_show]
            .reset_index()
            .rename(columns={"count": "total_count"})
        )

        ax.barh(
            y=df_plot["predictor"],
            width=df_plot["total_count"],
            color=df_plot["color"],
            edgecolor="dimgray",
        )
        ax.invert_yaxis()
        ax.set_title(f"{cluster_name}", fontsize=13, loc="left", fontstyle="italic")
        ax.set_xlabel(f"#appearance as top-{top_n}")
        # increase y ticks font size
        ax.set_ylabel(None)
        ax.tick_params(labelsize=12)

    # Hide any extra axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    # fig.suptitle(f"Top {top_n} incMSE% count, across signatures", fontsize=14)
    fig.suptitle("(b)", fontsize=14, x=0.0)
    # fig.suptitle(f"Top {top_n} incMSE% count, across signatures", fontsize=14)
    out_grid = f"incMSE_count_top{top_n}_all_signatures_by_clusters.{file_type}"
    fig.savefig(os.path.join(fig_dir, out_grid), dpi=300, bbox_inches="tight")
    # plt.close(fig)


plot_counts_by_cluster(
    df_top_counts,
    clusters=clusters[1:],
    cluster_names=cluster_names[1:],
    top_k_features=12,
    top_n=top_n,
)

#############################################################
# BY BROADER REGIONS
#############################################################
# Rank absolute SHAP within each gauge and signature, then flag top-N
print("Ranking absolute SHAP values...")
# Rank %IncMSE within each predictor, signature and cluster group
df_imp["rank_by_region"] = df_imp.groupby(["sig_name", "region"])["%IncMSE"].rank(
    method="first", ascending=False
)

# Flag top-N
df_imp["is_top_n"] = (df_imp["rank_by_region"] <= top_n).astype(int)
df_imp.head()
# %% #########################################################
# Count the score per region
#############################################################

# Aggregate counts of top-N occurrences per cluster per attribute, across signatures
print(f"Counting top-{top_n} SHAP values per region...")
grouping_col = "region"
df_top_counts = (
    df_imp[df_imp["is_top_n"] == 1]
    .groupby([grouping_col, "predictor"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts.head()

# %% #########################################################
# Show and save the table for the top 10 SHAP values per region
#############################################################

print(f"Showing and saving the table for the top {show_k} incMSE values per region...")
for region in regions:
    print(f"{region} — top {top_n} attributes by incMSE-count:")
    # Subset the data
    dfc = df_top_counts[df_top_counts["region"] == region].sort_values(
        "count", ascending=False
    )
    top_attrs = dfc.head(show_k)
    # print(f"{cluster} - {cluster_name} — top {top_n} attributes by incMSE-count:")
    if top_attrs.empty:
        print("  (no data)")
    else:
        print(top_attrs[["predictor", "count"]].to_string(index=False))
    print("--------------------------------")

# Out put them as csv file
df_top_counts.to_csv(
    os.path.join(fig_dir, f"top{top_n}_attrs_by_incMSE_count_region.csv"), index=False
)


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
            df = df.merge(
                attrs_info, how="left", left_on="predictor", right_on="variable_name"
            )
            df["color"] = df["Group"].map(attrs_colors)

        # Aggregate total counts per feature and group, keep color/group for each feature
        df.sort_values("count", ascending=False, inplace=True)
        predictors_to_show = list(df.index[:top_k_features])

        # Build plotting frame
        # Select the top features
        df_plot = (
            df.loc[predictors_to_show]
            .reset_index()
            .rename(columns={"count": "total_count"})
        )

        ax.barh(
            y=df_plot["predictor"],
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

    fig.suptitle(f"Top {top_n} incMSE% count, across signatures", fontsize=14)
    out_grid = f"incMSE_count_top{top_n}_all_signatures_by_broader_regions.{file_type}"
    fig.savefig(os.path.join(fig_dir, out_grid), dpi=300, bbox_inches="tight")
    # plt.close(fig)


plot_counts_by_region(
    df_top_counts,
    regions=regions,
    top_k_features=12,
    top_n=top_n,
)

# %%
