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

# %%
########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
# rf_out_dir = os.path.join(rf_dir, "output_raraki_20250826_cluster_all")
output_date = "20250826"
# fig_dir = os.path.join(rf_dir, "output_raraki_20250826_figures")
output_date_Wu = "20250827"
# rf_out_dir_Wu = os.path.join(rf_dir, "output_raraki_20250827_cluster_all_Wu")
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
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
with open("plot_config_attrs_colors.json", "r") as file:
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


def load_r2_by_cluster(rf_dir, user_name, output_date, output_date_Wu, cluster_info):
    _dfs_r2 = []

    # Read by cluster_num
    for cluster_num in cluster_info.keys():
        file_path = os.path.join(
            rf_dir,
            f"output_{user_name}_{output_date}_cluster_{cluster_num}",
            "r_squared_all.csv",
        )
        file_path_Wu = os.path.join(
            rf_dir,
            f"output_{user_name}_{output_date_Wu}_cluster_{cluster_num}_Wu",
            "r_squared_all.csv",
        )

        if os.path.exists(file_path) and os.path.exists(file_path_Wu):
            _df_temp = pd.read_csv(file_path, index_col="sig_name")
            _df_temp_Wu = pd.read_csv(file_path_Wu, index_col="sig_name")
            df_temp = pd.concat([_df_temp, _df_temp_Wu], axis=0)
            df_temp["cluster_num"] = cluster_num
            # if cluster_num == "all":
            #     df_temp.columns = ["CONUS-wide"]
            # else:
            #     df_temp.columns = [
            #         f"{cluster_num} - {cluster_info[cluster_num]['name']}"
            #     ]
            _dfs_r2.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs_r2 = pd.concat(_dfs_r2, axis=0)
    return dfs_r2


def load_r2_all(rf_dir, user_name, output_date, output_date_Wu):
    file_path = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date}_cluster_all",
        "r_squared_all.csv",
    )
    file_path_Wu = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date_Wu}_cluster_all_Wu",
        "r_squared_all.csv",
    )
    if os.path.exists(file_path) and os.path.exists(file_path_Wu):
        _df_r2 = pd.read_csv(file_path, index_col="sig_name")
        _df_r2_Wu = pd.read_csv(file_path_Wu, index_col="sig_name")
        df_r2 = pd.concat([_df_r2, _df_r2_Wu], axis=0)
    else:
        print(f"File not found: {file_path}")
        print(f"File not found: {file_path_Wu}")

    return df_r2


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


def load_shap_by_cluster(
    rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
):
    file_path = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date}_cluster_{cluster_num}",
        "shap_values.csv",
    )
    file_path_Wu = os.path.join(
        rf_dir,
        f"output_{user_name}_{output_date_Wu}_cluster_{cluster_num}_Wu",
        "shap_values.csv",
    )

    _shap_df = pd.read_csv(file_path)
    _shap_df_Wu = pd.read_csv(file_path_Wu)

    df_shap = pd.concat([_shap_df, _shap_df_Wu], axis=0)

    # Convert to float
    df_shap["feature_value"] = df_shap["feature_value"].astype(float)
    df_shap["phi"] = df_shap["phi"].astype(float)
    df_shap["phi.var"] = df_shap["phi.var"].astype(float)

    # Merge with attributes info
    df_shap = df_shap.merge(
        attrs_info, how="left", left_on="feature", right_on="variable_name"
    )
    return df_shap


# %%
######################################################
# R-squares comparison by region
#####################################################


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


dfs_r2 = load_r2_all(rf_dir, user_name, output_date, output_date_Wu)

plot_r2_conus_wide(dfs_r2)

# %% ################################################
# Attributes importance by incMSE
#####################################################


# Function to plot bar plots
def plot_incMSE(df, cluster_num, cluster_info):
    # sigs = df["sig_name"].unique()
    sigs = sigs_RF_names_ordered  # When you want to subset the signatures

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
        df_subset = df[df["sig_name"] == sig].sort_values(by="%IncMSE", ascending=False)
        sns.barplot(
            data=df_subset,
            x="%IncMSE",
            y="predictor",
            hue="predictor",
            palette=color_dict,
            ax=axes[i],
        )
        axes[i].set_title(sig, loc="left", fontsize=30)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(cluster_name, fontsize=24)
    # fig.subplots_adjust(top=0.9)
    fig.savefig(
        os.path.join(fig_dir, f"incMSE_importance_bar_{cluster_num}.{file_type}"),
        dpi=1200,
    )


# #####################################################
# incMSE (bar plots, individual attributes)
# #####################################################

for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    df_imp = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
    )
    plot_incMSE(df_imp, cluster_num=cluster_num, cluster_info=cluster_info)


# %%
# Function to plot bar plots by category
def plot_incMSE_by_category(df, cluster_num, cluster_info):
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

        # Group by Group (category) and calculate mean incRMSE
        df_grouped = df_sig.groupby("Group")["%IncMSE"].mean().reset_index()

        # Sort by mean importance
        df_grouped = df_grouped.sort_values(by="%IncMSE", ascending=False)

        # Create color dictionary for groups
        colors = [attrs_colors.get(group, "lightgrey") for group in df_grouped["Group"]]

        # Plot
        sns.barplot(
            data=df_grouped,
            x="%IncMSE",
            y="Group",
            palette=dict(zip(df_grouped["Group"], colors)),
            ax=axes[i],
        )
        axes[i].set_title(sig, loc="left")
        # axes[i].set_ylabel(None)
        axes[i].set_xlabel("Mean variable importance")

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(f"Variable Importance by Category: {cluster_name}", fontsize=24)
    # fig.subplots_adjust(top=0.9)

    fig.savefig(
        os.path.join(fig_dir, f"incMSE_importance_cat_{cluster_num}.{file_type}"),
        dpi=1200,
    )


# #####################################################
# incMSE (bar plots, by category)
# #####################################################
for cluster_num in clusters:
    print(f"Processing category plots for {cluster_num}...")

    # Get data
    df_imp = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
    )

    # Plot
    plot_incMSE_by_category(df_imp, cluster_num=cluster_num, cluster_info=cluster_info)


# %% ###################################################
# incMSE (relative importance, by category)
########################################################


# Function to calculate and plot relative category importance across clusters
def plot_incMSE_relative_category(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each signature, creates a plot showing relative importance of each category
    across all clusters based on top ranked variables.

    Parameters:
    - rf_dir: Directory containing RF results
    - user_name: User name for file path
    - output_date: Date for file path
    - cluster_info: Dictionary with cluster information
    """
    # Get all signature names from one of the clusters
    sample_cluster = list(cluster_info.keys())[0]
    sample_data = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, sample_cluster, attrs_info
    )
    # all_signatures = sample_data["sig_name"].unique()
    all_signatures = sigs_RF_names_ordered  # When you want to subset the signatures

    # For each signature, create a plot that compares across clusters
    for sig_name in all_signatures:
        print(f"Processing signature: {sig_name}")

        # Collect data for each cluster
        cluster_data = []

        for cluster_num in cluster_info.keys():
            # Load data for this cluster
            df_imp = load_incMSE_by_cluster(
                rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
            )

            # Filter by signature
            df_sig = df_imp[df_imp["sig_name"] == sig_name].copy()

            # Group by category and sum importance
            category_imp = df_sig.groupby("Group")["%IncMSE"].sum().reset_index()

            # Calculate relative importance (percentage)
            total_imp = category_imp["%IncMSE"].sum()
            category_imp["rel_importance"] = category_imp["%IncMSE"] / total_imp * 100

            # Add cluster info
            category_imp["cluster_num"] = cluster_num
            if cluster_num == "all":
                category_imp["cluster_name"] = "CONUS-wide"
            else:
                category_imp["cluster_name"] = (
                    f"{cluster_num} - {cluster_info[cluster_num]['name']}"
                )

            cluster_data.append(category_imp)

        # Combine all cluster data
        combined_data = pd.concat(cluster_data, ignore_index=True)

        # Get all unique categories
        all_categories = combined_data["Group"].unique()

        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 6))

        # Set up colors for categories
        colors = [attrs_colors.get(group, "lightgrey") for group in all_categories]
        color_dict = dict(zip(all_categories, colors))

        # Get unique cluster names in order
        cluster_names = []
        for cluster_num in cluster_info.keys():
            if cluster_num == "all":
                cluster_names.append("CONUS-wide")
            else:
                cluster_names.append(
                    f"{cluster_num} - {cluster_info[cluster_num]['name']}"
                )

        # Create x positions for bars
        num_clusters = len(cluster_names)
        bar_width = 0.8
        x_positions = np.arange(num_clusters)

        # Initialize bottom values for stacking
        bottoms = np.zeros(num_clusters)

        # Sort categories by overall importance (optional)
        category_importance = {
            cat: combined_data[combined_data["Group"] == cat]["rel_importance"].mean()
            for cat in all_categories
        }
        sorted_categories = sorted(
            all_categories, key=lambda x: category_importance[x], reverse=True
        )

        # Plot each category as a stacked component
        for i, category in enumerate(sorted_categories):
            # Get data for this category across all clusters
            cat_data = combined_data[combined_data["Group"] == category]

            # Create array of importance values in cluster order
            values = []
            for cluster_name in cluster_names:
                cluster_value = cat_data[cat_data["cluster_name"] == cluster_name][
                    "rel_importance"
                ]
                values.append(cluster_value.iloc[0] if len(cluster_value) > 0 else 0)
            values = np.array(values)

            # Plot the stacked bars for this category
            bars = ax.bar(
                x_positions,
                values,
                width=bar_width,
                bottom=bottoms,
                label=category,
                color=color_dict[category],
                alpha=0.8,
                edgecolor="white",
            )

            # Update bottoms for next category
            bottoms += values

        # Customize the plot
        ax.set_title(
            f"Relative Category Importance for {sig_name}",
            fontsize=16,
        )
        ax.set_xlabel("Clusters", fontsize=12)
        ax.set_ylabel("Relative Importance (%)", fontsize=12)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(cluster_names, rotation=45, ha="right")
        ax.set_ylim(0, 105)

        # Add a legend
        ax.legend(
            title="Variable Categories", bbox_to_anchor=(1.05, 1), loc="upper left"
        )

        plt.tight_layout()
        plt.savefig(
            os.path.join(fig_dir, f"incMSE_relative_importance_{sig_name}.{file_type}"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close(fig)


# #####################################################
# incMSE (relative importance, by category)
# #####################################################
plot_incMSE_relative_category(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
)
# %%


# Function to calculate and plot relative category importance across clusters
def plot_incMSE_relative_category_allsignatures(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each signature, creates a plot showing relative importance of each category
    across all clusters based on top ranked variables.

    Parameters:
    - rf_dir: Directory containing RF results
    - user_name: User name for file path
    - output_date: Date for file path
    - cluster_info: Dictionary with cluster information
    """
    # Get all signature names from one of the clusters
    sample_cluster = list(cluster_info.keys())[0]
    sample_data = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, sample_cluster, attrs_info
    )
    # all_signatures = sample_data["sig_name"].unique()
    all_signatures = sigs_RF_names_ordered  # When you want to subset the signatures

    # For each signature, create a plot that compares across clusters
    for sig_name in all_signatures:
        print(f"Processing signature: {sig_name}")

        # Collect data for each cluster
        cluster_data = []

        for cluster_num in cluster_info.keys():
            # Load data for this cluster
            df_imp = load_incMSE_by_cluster(
                rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
            )

            # Filter by signature
            df_sig = df_imp[df_imp["sig_name"] == sig_name].copy()

            # Group by category and sum importance
            category_imp = df_sig.groupby("Group")["%IncMSE"].sum().reset_index()

            # Calculate relative importance (percentage)
            total_imp = category_imp["%IncMSE"].sum()
            category_imp["rel_importance"] = category_imp["%IncMSE"] / total_imp * 100

            # Add cluster info
            category_imp["cluster_num"] = cluster_num
            if cluster_num == "all":
                category_imp["cluster_name"] = "CONUS-wide"
            else:
                category_imp["cluster_name"] = (
                    f"{cluster_num} - {cluster_info[cluster_num]['name']}"
                )

            cluster_data.append(category_imp)

        # Combine all cluster data
        combined_data = pd.concat(cluster_data, ignore_index=True)

        # Get all unique categories
        all_categories = combined_data["Group"].unique()

        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 6))

        # Set up colors for categories
        colors = [attrs_colors.get(group, "lightgrey") for group in all_categories]
        color_dict = dict(zip(all_categories, colors))

        # Get unique cluster names in order
        cluster_names = []
        for cluster_num in cluster_info.keys():
            if cluster_num == "all":
                cluster_names.append("CONUS-wide")
            else:
                cluster_names.append(
                    f"{cluster_num} - {cluster_info[cluster_num]['name']}"
                )

        # Create x positions for bars
        num_clusters = len(cluster_names)
        bar_width = 0.8
        x_positions = np.arange(num_clusters)

        # Initialize bottom values for stacking
        bottoms = np.zeros(num_clusters)

        # Sort categories by overall importance (optional)
        category_importance = {
            cat: combined_data[combined_data["Group"] == cat]["rel_importance"].mean()
            for cat in all_categories
        }
        sorted_categories = sorted(
            all_categories, key=lambda x: category_importance[x], reverse=True
        )

        # Plot each category as a stacked component
        for i, category in enumerate(sorted_categories):
            # Get data for this category across all clusters
            cat_data = combined_data[combined_data["Group"] == category]

            # Create array of importance values in cluster order
            values = []
            for cluster_name in cluster_names:
                cluster_value = cat_data[cat_data["cluster_name"] == cluster_name][
                    "rel_importance"
                ]
                values.append(cluster_value.iloc[0] if len(cluster_value) > 0 else 0)
            values = np.array(values)

            # Plot the stacked bars for this category
            bars = ax.bar(
                x_positions,
                values,
                width=bar_width,
                bottom=bottoms,
                label=category,
                color=color_dict[category],
                alpha=0.8,
                edgecolor="white",
            )

            # Update bottoms for next category
            bottoms += values

        # Customize the plot
        ax.set_title(
            f"Relative Category Importance for {sig_name}",
            fontsize=16,
        )
        ax.set_xlabel("Clusters", fontsize=12)
        ax.set_ylabel("Relative Importance (%)", fontsize=12)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(cluster_names, rotation=45, ha="right")
        ax.set_ylim(0, 105)

        # Add a legend
        ax.legend(
            title="Variable Categories", bbox_to_anchor=(1.05, 1), loc="upper left"
        )

        plt.tight_layout()
        plt.savefig(
            os.path.join(fig_dir, f"incMSE_relative_importance_{sig_name}.{file_type}"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close(fig)


# #####################################################
# incMSE (relative importance, by category)
# #####################################################
plot_incMSE_relative_category_allsignatures(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
)

# %% ###################################################
# incMSE (category delta vs CONUS-wide)
########################################################


def _compute_rel_importance_by_category(df_imp, sig_name):
    df_sig = df_imp[df_imp["sig_name"] == sig_name].copy()
    cat_sum = df_sig.groupby("Group")["%IncMSE"].sum()
    total = cat_sum.sum()
    if total == 0 or np.isnan(total):
        return cat_sum * 0
    return cat_sum / total * 100.0


def plot_incMSE_category_delta_vs_conus(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each regional cluster (excluding CONUS-wide), create one figure with
    subplots for all signatures. Each subplot shows category-wise delta (pp)
    vs CONUS-wide.
    """

    # Load CONUS baseline once
    df_all = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, "all", attrs_info
    )

    # Use the configured category list for consistent ordering across subplots
    all_cats = list(attrs_colors.keys())[::-1]
    bar_colors = [attrs_colors.get(cat, "lightgrey") for cat in all_cats]

    for cluster_num in cluster_info.keys():
        if cluster_num == "all":
            continue

        # Pre-compute deltas for all signatures for this cluster
        df_reg = load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
        )

        deltas = {}
        max_abs_delta = 0.0
        for sig_name in sigs_RF_names_ordered:
            baseline_rel = _compute_rel_importance_by_category(df_all, sig_name)
            reg_rel = _compute_rel_importance_by_category(df_reg, sig_name)
            delta = reg_rel.reindex(all_cats, fill_value=np.nan) - baseline_rel.reindex(
                all_cats, fill_value=np.nan
            )
            deltas[sig_name] = delta
            max_abs_delta = max(
                max_abs_delta, float(delta.abs().max() if len(delta) else 0.0)
            )

        print("--------------------------------")
        print("Cluster: ", cluster_num)
        print("Delta:")
        print(deltas)
        print("--------------------------------")

        # Figure layout
        n_cols = 4
        n_rows = (len(sigs_RF_names_ordered) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(
            nrows=n_rows,
            ncols=n_cols,
            figsize=(4 * n_cols, 2.6 * n_rows),
            constrained_layout=True,
        )
        axes = axes.flatten()

        # Symmetric x-limits shared across subplots
        x_margin = max(3.0, max_abs_delta * 0.1)
        xlim = (-max_abs_delta - x_margin, max_abs_delta + x_margin)

        for i, sig_name in enumerate(sigs_RF_names_ordered):
            ax = axes[i]
            delta = deltas[sig_name]
            ax.barh(all_cats, delta.values, color=bar_colors, alpha=0.9)
            ax.axvline(0, color="k", linestyle="--", linewidth=0.6, alpha=0.7)
            ax.set_title(sig_name, fontsize=9, loc="left")
            ax.set_xlim(xlim)
            if i % n_cols != 0:
                ax.set_yticklabels([])
            else:
                ax.set_ylabel("Category", fontsize=9)
            if i // n_cols == n_rows - 1:
                ax.set_xlabel("Delta (pp)", fontsize=9)

        # Hide any unused axes
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
        # fig.suptitle(f"Category delta vs CONUS-wide — {cluster_name}", fontsize=14)

        plt.savefig(
            os.path.join(
                fig_dir,
                f"incMSE_category_delta_vs_conus_cluster_{cluster_num}.{file_type}",
            ),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close(fig)


# #####################################################
# incMSE (category delta vs CONUS-wide) — subplots
# #####################################################
plot_incMSE_category_delta_vs_conus(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
)

# %% ###################################################
# incMSE (category delta vs CONUS-wide)
########################################################


def plot_incMSE_category_delta_vs_conus__sigs(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each regional cluster (excluding CONUS-wide), create one figure with
    subplots for all signatures. Each subplot shows category-wise delta (pp)
    vs CONUS-wide.
    """

    # Load CONUS baseline once
    df_all = load_incMSE_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, "all", attrs_info
    )

    # Use the configured category list for consistent ordering across subplots
    all_cats = list(attrs_colors.keys())[::-1]
    bar_colors = [attrs_colors.get(cat, "lightgrey") for cat in all_cats]

    list_deltas = []
    for cluster_num in cluster_info.keys():
        if cluster_num == "all":
            continue

        # Pre-compute deltas for all signatures for this cluster
        df_reg = load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
        )

        deltas = pd.DataFrame()

        for sig_name in sigs_RF_names_ordered:
            baseline_rel = _compute_rel_importance_by_category(df_all, sig_name)
            reg_rel = _compute_rel_importance_by_category(df_reg, sig_name)
            delta = reg_rel.reindex(all_cats, fill_value=np.nan) - baseline_rel.reindex(
                all_cats, fill_value=np.nan
            )

            delta_df = pd.DataFrame(
                {
                    "delta": delta.values,
                    "cluster_num": cluster_num,
                    "sig_name": sig_name,
                    "category": all_cats,
                }
            )
            list_deltas.append(
                delta_df
            )  # or list_deltas.append(delta_df.copy(deep=True))
            print("--------------------------------")
            print(sig_name)
            print(delta_df)
            print("--------------------------------")

    df_deltas = pd.concat(list_deltas)
    df_deltas.to_csv(os.path.join(fig_dir, "deltas.csv"), index=False)

    # Figure layout
    n_cols = 3
    n_rows = 2
    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(4 * n_cols, 3.2 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()
    plt.rcParams.update({"font.size": 12})

    for i, cluster_num in enumerate(cluster_info.keys()):
        if cluster_num == "all":
            continue

        # Symmetric x-limits shared across subplots
        x_margin = max(3.0, 12.0)
        xlim = (-x_margin, x_margin)

        df_cluster = df_deltas[df_deltas["cluster_num"] == cluster_num].copy()
        deltas_mean_across_sigs = df_cluster.groupby("category")["delta"].median()
        deltas_mean_across_sigs = deltas_mean_across_sigs.reindex(all_cats)

        ax = axes[i]
        ax.barh(
            deltas_mean_across_sigs.index,
            deltas_mean_across_sigs.values,
            color=bar_colors,
            alpha=0.9,
            edgecolor="dimgrey",
        )
        ax.axvline(0, color="k", linestyle="--", linewidth=0.6, alpha=0.7)
        ax.set_title(cluster_dict[cluster_num], fontsize=13, loc="left", style="italic")
        ax.set_xlim(xlim)
        ax.set_xlabel(r"Median $\Delta RI_{k}$ (%)", fontsize=12)
        ax.tick_params(labelsize=12)

    # fig.suptitle(
    #     # f"Changes in variable importance in regional experiments, compared to CONUS-wide experiment",
    #     fontsize=14,
    # )

    plt.savefig(
        os.path.join(
            fig_dir,
            f"incMSE_category_delta_vs_conus_cluster_mean_across_sigs.{file_type}",
        ),
        dpi=300,
        bbox_inches="tight",
    )
    # plt.close(fig)


# #####################################################
# incMSE (category delta vs CONUS-wide) — subplots
# #####################################################
cluster_dict = {
    3: "Pacific Northwest",
    0: "Midwest",
    5: "Northeast",
    4: "Western Coast and Deserts",
    2: "Mountain West",
    1: "South",
}
plot_incMSE_category_delta_vs_conus__sigs(
    rf_dir, user_name, output_date, output_date_Wu, cluster_dict
)


# %%
cluster_info.keys()

# %% ###################################################
# SHAP values
#######################################################


# ##################################################
# SHAP values (bar plots, individual attributes)
########################################################


# Function to plot bar plots
def plot_shap(df, cluster_num, cluster_info):
    # sigs = df["sig_name"].unique()
    sigs = sigs_RF_names_ordered  # When you want to subset the signatures
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

for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    df_shap = load_shap_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
    )
    plot_shap(df_shap, cluster_num=cluster_num, cluster_info=cluster_info)


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

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(f"Variable Importance by Category: {cluster_name}", fontsize=24)
    # fig.subplots_adjust(top=0.9)

    fig.savefig(
        os.path.join(fig_dir, f"shap_cat_{cluster_num}.{file_type}"),
        dpi=1200,
    )


# #####################################################
# Shapley (bar plots, by category)
# #####################################################

for cluster_num in clusters:
    print(f"Processing category plots for {cluster_num}...")

    # Get data
    df_shap = load_shap_by_cluster(
        rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
    )

    # Plot
    plot_shap_by_category(df_shap, cluster_num=cluster_num, cluster_info=cluster_info)

# %% ###################################################
# PLOT SHAP IN A MAP
########################################################

print("Loading SHAP data...")
df_shap = load_shap_by_cluster(
    rf_dir, user_name, output_date, output_date_Wu, "all", attrs_info
)
df_shap["gauge_id"] = df_shap["gauge_id"].astype(str)

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


# %%
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
# SHAP % IN A MAP
#####################################################
# Plot the relative contribution of each attribute to the signature
for sig_name in tqdm(sigs_RF_names_ordered[:-2], desc="Processing SHAP in map"):
    plot_shap_in_map(df_shap_with_attrs, sig_name, "phi_perc")


# %% Sometimes the loop runs out of memory, here to redo it manually
for sig_name in ["R_Pint_RC", "R_Pvol_RC"]:
    print(f"Processing {sig_name}...")
    plot_shap_in_map(df_shap_with_attrs, sig_name, "phi_perc")


# %% ###################################################
# PLOT SHAP VS ATTRIBUTE
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


def plot_shap_in_map_max(df_group_max, sig_name, varname="max_mean  _phi_abs_perc"):
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

    # Plot the max category per location
    max_opacity = df_group_max[varname].quantile(0.90)
    scatter_obj = ax.scatter(
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


# %% Get the average contributions from 2 signatures and plot the max category per location
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
        "Process": "Overland flow (IE vs. SE)",
        "sigs": ["R_Pint_RC", "R_Pvol_RC"],
    },
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
        )
        .reset_index()
    ).rename(columns={"mean_phi_abs_perc": f"{stat}_phi_abs_perc_sigs"})

    # For each gauge_id, get the row with the maximum phi_abs_perc
    df_group_avg_max = (
        df_group_avg.loc[
            df_group_avg.groupby("gauge_id")[f"{stat}_phi_abs_perc_sigs"].idxmax()
        ][["gauge_id", f"{stat}_phi_abs_perc_sigs", "Group", "gauge_lon", "gauge_lat"]]
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
