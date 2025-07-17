# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %%
########################## CHANGE HERE #################
output_date = r"20250715"
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

# Current director
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

# Set up Figure output directory
rf_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf"
fig_dir = os.path.join(rf_dir, f"output_{user_name}_{output_date}_figures")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


# Get Random Forest output directory name
def output_dir_name(rf_dir, user_name, output_date, cluster_num):
    if not isinstance(cluster_num, (int, float)):
        output_dir = (
            f"output_{user_name}_{output_date}_cluster_{cluster_num}"  # For regional
        )
    else:
        output_dir = f"output_{user_name}_{output_date}_cluster_{cluster_num}"
    return os.path.join(rf_dir, output_dir)


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

# Cluster colors
with open("plot_config_expcolors_clusters.json", "r") as file:
    cluster_plot_json = json.load(file)
# Convert keys to integers except for the first item
cluster_info = {int(k) if k.isdigit() else k: v for k, v in cluster_plot_json.items()}
clusters = cluster_info.keys()
print(clusters)


# ____________________________________________________________________________________
# Attributes
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


# Function to map colors
def map_colors(group):
    return attrs_colors.get(group, "lightgrey")


# Function to create color dictionary
def create_color_dict(df, var_name):
    df["color"] = df["Group"].apply(map_colors)
    return df.set_index(var_name)["color"].to_dict()


# %%
######################################################
# R-squares comparison by region
#####################################################


def load_data_r2(rf_dir, user_name, output_date, cluster_info):
    _dfs_r2 = []

    # Read by cluster_num
    for cluster_num in cluster_info.keys():
        output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)
        file_path = os.path.join(output_dir, "r_squared.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="sig_name")
            if cluster_num == "all":
                df_temp.columns = ["CONUS-wide"]
            else:
                df_temp.columns = [
                    f"{cluster_num} - {cluster_info[cluster_num]['name']}"
                ]
            _dfs_r2.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs_r2 = pd.concat(_dfs_r2, axis=1)
    return dfs_r2


def plot_r2(df, cluster_info):
    # Plotting the multiple bar plot
    colors = [
        cluster_info[cluster_num]["color"]
        for cluster_num in cluster_info.keys()
        if f"{cluster_num} - {cluster_info[cluster_num]['name']}" in df.columns
    ]
    colors.insert(0, "lightgrey")

    fig, ax = plt.subplots(figsize=(20, 8))
    df.plot(kind="bar", color=colors, ax=ax)
    ax.set_title(r"$R^2$ for Different cluster_nums")
    ax.set_xlabel("Signature")
    ax.set_ylabel(r"$R^2$")
    ax.set_xticklabels(df.index, rotation=45, ha="right")
    ax.legend(title="cluster_nums", bbox_to_anchor=(1.05, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(
        os.path.join(fig_dir, f"r2_per_sig.{file_type}"), dpi=300
    )  # Save as PNG or PDF


def plot_avg_r2(dfs_r2, cluster_info):
    df_avg_r2 = dfs_r2.mean(axis=0).reset_index()
    df_avg_r2.columns = ["cluster_name", "Average R-squared"]

    df_avg_r2["cluster_num"] = df_avg_r2["cluster_name"].apply(
        lambda x: int(x.split(" - ")[0]) if " - " in x else x
    )

    df_avg_r2["Color"] = df_avg_r2["cluster_num"].apply(
        lambda x: cluster_info[int(x)]["color"]
        if x != "CONUS-wide" and int(x) in cluster_info
        else "lightgrey"
    )

    fig, ax = plt.subplots(figsize=(4, 5))
    ax.bar(
        df_avg_r2["cluster_name"],
        df_avg_r2["Average R-squared"],
        color=df_avg_r2["Color"],
    )
    ax.set_title(r"Average $R^2$ for Different cluster_nums")
    ax.set_xlabel("cluster name")
    ax.set_ylabel(r"Average $R^2$")
    ax.set_xticklabels(df_avg_r2["cluster_name"], rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(
        os.path.join(fig_dir, f"r2_average.{file_type}"), dpi=300
    )  # Save as PNG or PDF}"))
    df_avg_r2.to_csv(os.path.join(fig_dir, "r2_average.csv"), index=True)


dfs_r2 = load_data_r2(rf_dir, user_name, output_date, cluster_info)
plot_r2(dfs_r2, cluster_info)
plot_avg_r2(dfs_r2, cluster_info)


# %%

######################################################
# Attributes importance by incRMSE
#####################################################


# Function to load data
def load_data_incMSE(rf_dir, user_name, output_date, cluster_num, attrs_info):
    output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)

    _df_imp = pd.read_csv(os.path.join(output_dir, "var_importance.csv"))

    df_imp = _df_imp.merge(
        attrs_info, how="left", left_on="predictor", right_on="variable_name"
    )

    return df_imp


# Function to plot bar plots
def plot_incMSE(df, cluster_num, cluster_info):
    sigs = df["sig_name"].unique()
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
    fig.subplots_adjust(top=0.9)
    fig.savefig(
        os.path.join(fig_dir, f"var_importance_bar_{cluster_num}.{file_type}"),
        dpi=1200,
    )


######################################################
# incRMSE (bar plots, individual attributes)
#####################################################

for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    df_imp = load_data_incMSE(rf_dir, user_name, output_date, cluster_num, attrs_info)
    plot_incMSE(df_imp, cluster_num=cluster_num, cluster_info=cluster_info)


# %%
# Function to plot bar plots by category
def plot_incMSE_by_category(df, cluster_num, cluster_info, subset_top=False, top_n=10):
    sigs = df["sig_name"].unique()

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

        # First sort by importance and take only top 10 variables
        if subset_top:
            top_10_vars = df_sig.sort_values(by="%IncMSE", ascending=False).head(top_n)

            # Now group these top 10 variables by category and calculate mean
            df_grouped = top_10_vars.groupby("Group")["%IncMSE"].mean().reset_index()

            # Sort categories by mean importance
            df_grouped = df_grouped.sort_values(by="%IncMSE", ascending=False)

        else:
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
    fig.subplots_adjust(top=0.9)
    if subset_top:
        fig.savefig(
            os.path.join(
                fig_dir, f"var_importance_cat_top{top_n}_{cluster_num}.{file_type}"
            ),
            dpi=1200,
        )
    else:
        fig.savefig(
            os.path.join(fig_dir, f"var_importance_cat_{cluster_num}.{file_type}"),
            dpi=1200,
        )


######################################################
# incRMSE (bar plots, by category)
#####################################################
for cluster_num in clusters:
    print(f"Processing category plots for {cluster_num}...")

    # Get data
    df_imp = load_data_incMSE(rf_dir, user_name, output_date, cluster_num, attrs_info)

    # Plot
    plot_incMSE_by_category(df_imp, cluster_num=cluster_num, cluster_info=cluster_info)


# %%
# Function to calculate and plot relative category importance across clusters
def plot_incMSE_relative_category(
    rf_dir, user_name, output_date, cluster_info, subset_top=False, top_n=10
):
    """
    For each signature, creates a plot showing relative importance of each category
    across all clusters based on top ranked variables.

    Parameters:
    - rf_dir: Directory containing RF results
    - user_name: User name for file path
    - output_date: Date for file path
    - cluster_info: Dictionary with cluster information
    - top_n: Number of top variables to consider (default 10)
    """
    # Get all signature names from one of the clusters
    sample_cluster = list(cluster_info.keys())[0]
    sample_data = load_data_incMSE(
        rf_dir, user_name, output_date, sample_cluster, attrs_info
    )
    all_signatures = sample_data["sig_name"].unique()

    # For each signature, create a plot that compares across clusters
    for sig_name in all_signatures:
        print(f"Processing signature: {sig_name}")

        # Collect data for each cluster
        cluster_data = []

        for cluster_num in cluster_info.keys():
            # Load data for this cluster
            df_imp = load_data_incMSE(
                rf_dir, user_name, output_date, cluster_num, attrs_info
            )

            # Filter by signature
            df_sig = df_imp[df_imp["sig_name"] == sig_name].copy()

            if subset_top:
                # Get top N variables by importance
                top_vars = df_sig.sort_values(by="%IncMSE", ascending=False).head(top_n)

                # Group by category and sum importance
                category_imp = top_vars.groupby("Group")["%IncMSE"].sum().reset_index()

            else:
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
                bottom=bottoms,  # This ensures bars are stacked on top of previous ones
                label=category,
                color=color_dict[category],
                alpha=0.8,
                edgecolor="white",
            )

            # # Add category labels to the bars
            # for j, bar in enumerate(bars):
            #     if values[j] > 5:  # Only label if importance > 5%
            #         ax.text(
            #             bar.get_x() + bar.get_width() / 2,
            #             bottoms[j]
            #             + values[j] / 2,  # Position text in middle of segment
            #             f"{category}",
            #             ha="center",
            #             va="center",
            #             color="white",
            #             fontweight="bold",
            #             fontsize=8,
            #         )

            # Update bottoms for next category
            bottoms += values

        # Customize the plot
        if subset_top:
            title_suffix = f" (Top {top_n} Variables)"
        else:
            title_suffix = ""

        ax.set_title(
            f"Relative Category Importance for {sig_name} {title_suffix}",
            fontsize=16,
        )
        ax.set_xlabel("Clusters", fontsize=12)
        ax.set_ylabel("Relative Importance (%)", fontsize=12)
        ax.set_xticks(x_positions)
        ax.set_xticklabels(cluster_names, rotation=45, ha="right")
        ax.set_ylim(0, 105)  # Leave some space at top for labels

        # Add grid lines
        # ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Add a legend
        ax.legend(
            title="Variable Categories", bbox_to_anchor=(1.05, 1), loc="upper left"
        )

        plt.tight_layout()
        if subset_top:
            plt.savefig(
                os.path.join(
                    fig_dir,
                    f"relative_importance_top{top_n}_{sig_name}.{file_type}",
                ),
                dpi=300,
                bbox_inches="tight",
            )
        else:
            plt.savefig(
                os.path.join(fig_dir, f"relative_importance_{sig_name}.{file_type}"),
                dpi=300,
                bbox_inches="tight",
            )
        plt.close()


######################################################
# incRMSE (relative importance, by category)
#####################################################
plot_incMSE_relative_category(rf_dir, user_name, output_date, cluster_info)

# %%
# %%
# def plot_category_importance_difference(rf_dir, user_name, output_date, cluster_info):
#     """
#     For each signature, creates a plot showing the difference in relative importance
#     between CONUS-wide and each cluster for each attribute category.

#     Parameters:
#     - rf_dir: Directory containing RF results
#     - user_name: User name for file path
#     - output_date: Date for file path
#     - cluster_info: Dictionary with cluster information
#     """
#     # Get all signature names from the CONUS-wide cluster
#     all_data = load_data_incMSE(rf_dir, user_name, output_date, "all", attrs_info)
#     all_signatures = all_data["sig_name"].unique()

#     # Get all regional clusters (excluding "all")
#     regional_clusters = [c for c in cluster_info.keys() if c != "all"]

#     # Process each signature
#     for sig_name in all_signatures:
#         print(f"Processing differences for signature: {sig_name}")

#         # Get CONUS-wide data for this signature
#         df_all = all_data[all_data["sig_name"] == sig_name].copy()

#         # Calculate total importance per category for CONUS-wide
#         total_imp_all = df_all["%IncMSE"].sum()
#         category_imp_all = df_all.groupby("Group")["%IncMSE"].sum().reset_index()
#         category_imp_all["rel_importance"] = (
#             category_imp_all["%IncMSE"] / total_imp_all * 100
#         )

#         # Get all unique categories from CONUS-wide data
#         all_categories = category_imp_all["Group"].unique()

#         # Create a dict to store CONUS-wide relative importance by category
#         conus_imp = dict(
#             zip(category_imp_all["Group"], category_imp_all["rel_importance"])
#         )

#         # Set up the figure with subplots for each cluster
#         fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharex=True, sharey=True)
#         axes = axes.flatten()

#         # Create colors for categories (use red for positive differences, blue for negative)
#         colors = [attrs_colors.get(group, "lightgrey") for group in all_categories]
#         color_dict = dict(zip(all_categories, colors))

#         # Process each regional cluster
#         for i, cluster_num in enumerate(regional_clusters):
#             ax = axes[i]

#             # Load data for this cluster
#             df_cluster = load_data_incMSE(
#                 rf_dir, user_name, output_date, cluster_num, attrs_info
#             )
#             df_cluster = df_cluster[df_cluster["sig_name"] == sig_name].copy()

#             # Calculate total importance per category for this cluster
#             total_imp_cluster = df_cluster["%IncMSE"].sum()
#             category_imp_cluster = (
#                 df_cluster.groupby("Group")["%IncMSE"].sum().reset_index()
#             )
#             category_imp_cluster["rel_importance"] = (
#                 category_imp_cluster["%IncMSE"] / total_imp_cluster * 100
#             )

#             # Create a dict to store cluster's relative importance by category
#             cluster_imp = dict(
#                 zip(
#                     category_imp_cluster["Group"],
#                     category_imp_cluster["rel_importance"],
#                 )
#             )

#             # Calculate differences between CONUS-wide and this cluster
#             diff_data = []
#             for category in all_categories:
#                 conus_value = conus_imp.get(category, 0)
#                 cluster_value = cluster_imp.get(category, 0)
#                 diff = cluster_value - conus_value  # Cluster minus CONUS-wide
#                 diff_data.append(
#                     {
#                         "Category": category,
#                         "Difference": diff,
#                         "Color": color_dict[category],
#                     }
#                 )

#             # Create DataFrame from differences and sort by absolute difference
#             diff_df = pd.DataFrame(diff_data)
#             diff_df = diff_df.sort_values(by="Difference", key=abs, ascending=False)

#             # Plot the differences as horizontal bars
#             bars = ax.barh(
#                 diff_df["Category"],
#                 diff_df["Difference"],
#                 color=diff_df["Color"],
#                 alpha=0.8,
#                 edgecolor="black",
#                 linewidth=0.5,
#             )

#             # Add a vertical line at x=0
#             ax.axvline(x=0, color="black", linestyle="-", alpha=0.3)

#             # Add value labels to the bars
#             for bar in bars:
#                 width = bar.get_width()
#                 label_x_pos = width if width >= 0 else width - 1.5
#                 ax.text(
#                     label_x_pos,
#                     bar.get_y() + bar.get_height() / 2,
#                     f"{width:.1f}%",
#                     va="center",
#                     fontsize=8,
#                     fontweight="bold",
#                 )

#             # Set title and format axes
#             ax.set_title(
#                 f"Cluster {cluster_num} - {cluster_info[cluster_num]['name']}",
#                 fontsize=10,
#             )
#             ax.set_xlabel("Difference in Relative Importance (%)")

#             if i == 0 or i == 3:  # Only show y labels for left plots
#                 ax.set_ylabel("Category")
#             else:
#                 ax.set_ylabel("")

#         # Hide any unused subplots
#         for j in range(len(regional_clusters), len(axes)):
#             axes[j].set_visible(False)

#         # Add a main title
#         fig.suptitle(
#             f"Difference in Category Importance: Regional Clusters vs. CONUS-wide\n{sig_name}",
#             fontsize=16,
#             y=1.02,
#         )

#         # Add explanatory text
#         fig.text(
#             0.5,
#             0.01,
#             "Positive values: Category is MORE important in regional cluster\n"
#             "Negative values: Category is LESS important in regional cluster",
#             ha="center",
#             fontsize=10,
#         )

#         # Adjust layout and save
#         plt.tight_layout()
#         plt.savefig(
#             os.path.join(fig_dir, f"category_importance_diff_{sig_name}.{file_type}"),
#             dpi=300,
#             bbox_inches="tight",
#         )
#         plt.close()


# # Run the function
# plot_category_importance_difference(rf_dir, user_name, output_date, cluster_info)

# %%

######################################################
# SHAP values
#####################################################


def load_shap(rf_dir, user_name, output_date, cluster_num, attrs_info):
    output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)
    _shap_df = pd.read_csv(os.path.join(output_dir, "shap_values.csv"))

    # Convert to float
    _shap_df["feature_value"] = _shap_df["feature_value"].astype(float)
    _shap_df["phi"] = _shap_df["phi"].astype(float)
    _shap_df["phi.var"] = _shap_df["phi.var"].astype(float)

    # Merge with attributes info
    shap_df = _shap_df.merge(
        attrs_info, how="left", left_on="feature", right_on="variable_name"
    )
    return shap_df


# Function to plot bar plots
def plot_shap(df, cluster_num, cluster_info):
    sigs = df["sig_name"].unique()
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


######################################################
# SHAP values (bar plots, individual attributes)
#####################################################

# # CONUS-wide
# df_shap = load_shap(
#     rf_dir=rf_dir,
#     user_name=user_name,
#     output_date=output_date,
#     cluster_num="all",
#     attrs_info=attrs_info,
# )
# plot_shap(df=df_shap, cluster_num="all", cluster_info=cluster_info)

for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    df_shap = load_shap(rf_dir, user_name, output_date, cluster_num, attrs_info)
    plot_shap(df_shap, cluster_num=cluster_num, cluster_info=cluster_info)


# %% Function to plot bar plots by category
def plot_shap_by_category(df, cluster_num, cluster_info):
    sigs = df["sig_name"].unique()

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
    fig.subplots_adjust(top=0.9)

    fig.savefig(
        os.path.join(fig_dir, f"shap_cat_{cluster_num}.{file_type}"),
        dpi=1200,
    )


######################################################
# Shapley (bar plots, by category)
#####################################################
# # CONUS-wide
# df_shap = load_shap(
#     rf_dir=rf_dir,
#     user_name=user_name,
#     output_date=output_date,
#     cluster_num="all",
#     attrs_info=attrs_info,
# )
# plot_shap(df=df_shap, cluster_num="all", cluster_info=cluster_info)

for cluster_num in clusters:
    print(f"Processing category plots for {cluster_num}...")

    # Get data
    df_shap = load_shap(rf_dir, user_name, output_date, cluster_num, attrs_info)

    # Plot
    plot_shap_by_category(df_shap, cluster_num=cluster_num, cluster_info=cluster_info)

# %%
# %% ###################################################
# PLOT SHAP VS ATTRIBUTE
########################################################


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
        ax.scatter(
            df_sig_feature["feature_value"], df_sig_feature["phi"], alpha=0.5, s=9
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
    plt.close()


df_shap = load_shap(rf_dir, user_name, output_date, cluster_num, attrs_info)
for cluster_num in clusters:
    for sig_name in sigs_info["column_name"]:
        print(f"Processing {sig_name} for {cluster_num}...")
        plot_shap_vs_attr(df_shap, sig_name, cluster_num, cluster_info)


# %% ###################################################
# PLOT SHAP IN A MAP
########################################################

attrs_camels = pd.read_csv(attrs_camels_file)
attrs_hysets = pd.read_csv(attrs_hysets_file)
df_shap = load_shap(rf_dir, user_name, output_date, "all", attrs_info)

# Make sure all the gauge_id columns are string
df_shap["gauge_id"] = df_shap["gauge_id"].astype(str)
attrs_camels["gauge_id"] = attrs_camels["gauge_id"].astype(str)
attrs_hysets["gauge_id"] = attrs_hysets["gauge_id"].astype(str)

# %%
# Join df_SHAP with attrs_camels and attrs_hysets on gauge_id
df_shap_camels = df_shap.merge(attrs_camels, how="right", on="gauge_id")
df_shap_hysets = df_shap.merge(attrs_hysets, how="right", on="gauge_id")
df_shap_with_attrs = pd.concat([df_shap_camels, df_shap_hysets])

# %%
df_shap_with_attrs.head()


# %%
def plot_shap_in_map(df, sig_name):
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

        if df_sig["phi"].empty:
            continue

        # Limit the vmin and vmax based on the quantiles of the data
        vmin, vmax = np.quantile(df_sig["phi"], [0.20, 0.80])

        # Plot scatter
        df_sig_feature = df_sig[df_sig["feature"] == attr_name]
        scatter_obj = ax.scatter(
            df_sig_feature["gauge_lon"],
            df_sig_feature["gauge_lat"],
            c=df_sig_feature["phi"],
            alpha=0.5,
            s=9,
            zorder=99,
            vmin=vmin,
            vmax=vmax,
        )
        cbar = plt.colorbar(scatter_obj, ax=ax, shrink=0.3)
        cbar.set_label(r"$\phi$")
        ax.set_title(attr_name)

    fig.suptitle(sig_name, fontsize=24)

    # Save plot
    fig.savefig(
        os.path.join(fig_dir, f"shap_in_map_{sig_name}.{file_type}"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


for sig_name in sigs_info["column_name"]:
    print(f"Processing {sig_name}...")
    plot_shap_in_map(df_shap_with_attrs, sig_name)

# %%
