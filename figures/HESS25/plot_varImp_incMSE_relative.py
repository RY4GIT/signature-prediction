# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np

# %%
################## CHANGE HERE #############################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
output_date = "20250826"
output_date_Wu = "20250827"
user_name = "raraki"
file_type = "png"
########################################################

# ____________________________________________________________________________________
# I/O paths
fig_dir = os.path.join(cloud_dir, "figs", "fig_varImp")
sfig_dir = os.path.join(cloud_dir, "figs", "supfig_varImp")
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
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_attrs_colors.json",
    "r",
) as file:
    attrs_colors = json.load(file)

# Signature info
cofig_sigs_file = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_sigs.csv"
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
with open(
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_expcolors_clusters.json",
    "r",
) as file:
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


# %%
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


# %% ###################################################
# incMSE (category delta vs all clusters average)
########################################################


def _compute_rel_importance_by_category(df_imp, sig_name):
    df_sig = df_imp[df_imp["sig_name"] == sig_name].copy()
    cat_sum = df_sig.groupby("Group")["%IncMSE"].sum()
    total = cat_sum.sum()
    if total == 0 or np.isnan(total):
        return cat_sum * 0
    return cat_sum / total * 100.0


def plot_incMSE_category_delta_vs_avg(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each regional cluster (excluding CONUS-wide), create one figure with
    subplots for all signatures. Each subplot shows category-wise delta (pp)
    vs average across all clusters, excluding "all".
    """

    # Preload data for all regional clusters (exclude "all")
    regional_clusters = [c for c in cluster_info.keys() if c != "all" and c != "avg"]
    print("--------------------------------")
    print(regional_clusters)
    print("--------------------------------")
    df_by_cluster = {
        c: load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, c, attrs_info
        )
        for c in regional_clusters
    }

    # Use the configured category list for consistent ordering across subplots
    all_cats = list(attrs_colors.keys())[::-1]
    bar_colors = [attrs_colors.get(cat, "lightgrey") for cat in all_cats]

    # Compute baseline: mean relative importance across regional clusters for each signature
    baseline_rel_by_sig = {}
    for sig_name in sigs_RF_names_ordered:
        rel_list = []
        for c in regional_clusters:
            rel_list.append(
                _compute_rel_importance_by_category(df_by_cluster[c], sig_name)
            )
        if len(rel_list) > 0:
            baseline_rel_by_sig[sig_name] = pd.concat(rel_list, axis=1).mean(axis=1)
        else:
            baseline_rel_by_sig[sig_name] = pd.Series(dtype=float)

    print("--------------------------------")
    print("--------------------------------")
    print("-- CALCULATING DELTAS --")
    print("--------------------------------")
    print("--------------------------------")

    # Plot per cluster
    for cluster_num in cluster_info.keys():
        if cluster_num == "all" or cluster_num == "avg":
            continue

        # Pre-compute deltas for all signatures for this cluster
        df_reg = load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
        )

        deltas = {}
        max_abs_delta = 0.0
        for sig_name in sigs_RF_names_ordered:
            # Get baseline relative importance
            baseline_rel = baseline_rel_by_sig.get(sig_name, pd.Series(dtype=float))
            print("--------------------------------")
            print(f"Baseline for sig_name: {sig_name}")
            print(baseline_rel)
            print("--------------------------------")
            # Get regional relative importance
            reg_rel = _compute_rel_importance_by_category(df_reg, sig_name)
            print("--------------------------------")
            print(f"Regional {cluster_num} for sig_name: {sig_name}")
            print(reg_rel)
            print("--------------------------------")
            # Compute delta
            delta = reg_rel.reindex(all_cats, fill_value=np.nan) - baseline_rel.reindex(
                all_cats, fill_value=np.nan
            )
            print("--------------------------------")
            print(f"Delta for sig_name: {sig_name}")
            print(delta)
            print("--------------------------------")

            # Store delta
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
        n_cols = 3
        n_rows = 5
        fig, axes = plt.subplots(
            nrows=n_rows,
            ncols=n_cols,
            figsize=(4 * n_cols, 3.2 * n_rows),
            constrained_layout=True,
        )
        axes = axes.flatten()
        plt.rcParams.update({"font.size": 12})

        # Symmetric x-limits shared across subplots
        x_margin = max(3.0, max_abs_delta * 0.1)
        xlim = (-max_abs_delta - x_margin, max_abs_delta + x_margin)

        for i, sig_name in enumerate(sigs_RF_names_ordered):
            ax = axes[i]
            delta = deltas[sig_name]
            ax.barh(
                all_cats, delta.values, color=bar_colors, alpha=0.9, edgecolor="dimgrey"
            )
            ax.axvline(0, color="k", linestyle="--", linewidth=0.6, alpha=0.7)
            ax.set_title(sig_name, fontsize=13, loc="left", style="italic")
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

        fig.suptitle(
            f"{cluster_num} — {cluster_info[cluster_num]['name']}", fontsize=14
        )

        plt.savefig(
            os.path.join(
                sfig_dir,
                f"incMSE_category_delta_vs_avg_cluster_{cluster_num}.{file_type}",
            ),
            dpi=300,
            bbox_inches="tight",
        )
        # plt.close(fig)


# #####################################################
# incMSE (category delta vs all clusters average) — subplots
# #####################################################
plot_incMSE_category_delta_vs_avg(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
)

# %%
# ###################################################
# incMSE (category delta vs all clusters average)
########################################################


def plot_incMSE_category_delta_vs_avg__sigs(
    rf_dir, user_name, output_date, output_date_Wu, cluster_info
):
    """
    For each regional cluster (excluding CONUS-wide), create one figure with
    subplots for all signatures. Each subplot shows category-wise delta (pp)
    vs average across all clusters, excluding "all".
    """

    # Preload data for all regional clusters (exclude "all")
    regional_clusters = [c for c in cluster_info.keys() if c != "all" and c != "avg"]
    df_by_cluster = {
        c: load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, c, attrs_info
        )
        for c in regional_clusters
    }

    # Use the configured category list for consistent ordering across subplots
    all_cats = list(attrs_colors.keys())[::-1]
    bar_colors = [attrs_colors.get(cat, "lightgrey") for cat in all_cats]

    # Compute baseline: mean relative importance across regional clusters for each signature
    baseline_rel_by_sig = {}
    for sig_name in sigs_RF_names_ordered:
        rel_list = []
        for c in regional_clusters:
            rel_list.append(
                _compute_rel_importance_by_category(df_by_cluster[c], sig_name)
            )
        if len(rel_list) > 0:
            baseline_rel_by_sig[sig_name] = pd.concat(rel_list, axis=1).mean(axis=1)
        else:
            baseline_rel_by_sig[sig_name] = pd.Series(dtype=float)

    list_deltas = []
    for cluster_num in cluster_info.keys():
        if cluster_num == "all" or cluster_num == "avg":
            continue

        # Pre-compute deltas for all signatures for this cluster
        df_reg = load_incMSE_by_cluster(
            rf_dir, user_name, output_date, output_date_Wu, cluster_num, attrs_info
        )

        deltas = pd.DataFrame()

        for sig_name in sigs_RF_names_ordered:
            baseline_rel = baseline_rel_by_sig.get(sig_name, pd.Series(dtype=float))
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
    df_deltas.to_csv(os.path.join(sfig_dir, "deltas.csv"), index=False)

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
        if cluster_num == "all" or cluster_num == "avg":
            continue

        # Symmetric x-limits shared across subplots
        # x_margin = max(3.0, 12.0)
        xlim = (-7.0, 7.0)

        df_cluster = df_deltas[df_deltas["cluster_num"] == cluster_num].copy()
        deltas_mean_across_sigs = df_cluster.groupby("category")["delta"].mean()
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
        ax.set_xlabel(r"Mean $\Delta RI_{k}$ (%)", fontsize=12)
        ax.tick_params(labelsize=12)

    # fig.suptitle(
    #     # f"Changes in variable importance in regional experiments, compared to CONUS-wide experiment",
    #     fontsize=14,
    # )

    plt.savefig(
        os.path.join(
            sfig_dir,
            f"incMSE_category_delta_vs_avg_cluster_mean_across_sigs.{file_type}",
        ),
        dpi=300,
        bbox_inches="tight",
    )
    # plt.close(fig)


# #####################################################
# incMSE (category delta vs all clusters average) — subplots
# #####################################################
cluster_dict = {
    3: "Pacific Northwest",
    0: "Midwest and Central",
    5: "Northeast",
    4: "Southwest",
    2: "Mountain West",
    1: "South",
}
plot_incMSE_category_delta_vs_avg__sigs(
    rf_dir, user_name, output_date, output_date_Wu, cluster_dict
)
