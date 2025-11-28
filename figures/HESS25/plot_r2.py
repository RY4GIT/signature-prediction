# %% Plot R2 values from random forest experiments

import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np
import json

# %%
############## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
output_date = "20250826"
output_date_Wu = "20250827"
fig_dir = os.path.join(cloud_dir, "figs", "fig_r2")
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "png"
########################################################

# ____________________________________________________________________________________
# I/O paths

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# Plot config

with open(
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\config_expcolors_clusters.json",
    "r",
) as file:
    cluster_plot_json = json.load(file)
cluster_info = {int(k) if k.isdigit() else k: v for k, v in cluster_plot_json.items()}
clusters = cluster_info.keys()
print(clusters)


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
######################################################
# Data loader
#####################################################


def load_r2(rf_dir, user_name, cluster_num, output_date, output_date_Wu):
    # For general signatures
    output_dir = f"output_{user_name}_{output_date}_cluster_{cluster_num}"
    file_path = os.path.join(rf_dir, output_dir, "r_squared_all.csv")
    df_temp = pd.read_csv(file_path, index_col="sig_name")
    df_temp["cluster_num"] = cluster_num

    # For Wu's signatures
    output_dir = f"output_{user_name}_{output_date_Wu}_cluster_{cluster_num}_Wu"
    file_path = os.path.join(rf_dir, output_dir, "r_squared_all.csv")
    df_temp_Wu = pd.read_csv(file_path, index_col="sig_name")
    df_temp_Wu["cluster_num"] = cluster_num

    df_r2 = pd.concat([df_temp, df_temp_Wu], axis=0)

    return df_r2


# %%
######################################################
# R-squares comparison (All-CONUS model)
#####################################################


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


# %%
df_r2_all = load_r2(rf_dir, user_name, "all", output_date, output_date_Wu)
df_r2_all.head()


# %%
plot_r2_conus_wide(df_r2_all)


# %%
######################################################
# R-squares comparison (By region)
#####################################################


def plot_r2_regional(df_r2_by_region):
    # Create bar plot of R2 values for regional predictions
    fig, ax = plt.subplots(figsize=(10, 5))

    # Number of clusters and signatures
    n_sigs = len(sigs_RF_names_ordered)

    # Set width of bars and positions
    bar_width = 0.1
    index = np.arange(n_sigs)

    # Plot bars for each cluster
    for i, cluster in enumerate(["avg", 5, 1, 0, 2, 4, 3]):
        cluster_data = df_r2_by_region[df_r2_by_region["cluster_num"] == cluster]
        cluster_data = cluster_data.set_index("sig_name")
        print(cluster_data.head())

        # Get values in correct order
        r2_values = cluster_data.loc[sigs_RF_names_ordered, "r_squared_cv"]
        r2_std = cluster_data.loc[sigs_RF_names_ordered, "r_squared_cv_std"]

        # Plot bars
        ax.bar(
            index + i * bar_width,
            r2_values,
            bar_width,
            # yerr=r2_std,
            label=cluster_info[cluster]["name"],
            color=cluster_info[cluster]["color"],
            alpha=0.8,
            # error_kw={"ecolor": "dimgrey", "lw": 0.5, "capthick": 0.5, "capsize": 1},
        )

    # Customize plot
    ax.set_ylabel(r"$R^2$")
    ax.set_xticks(index + bar_width * 3)
    ax.set_xticklabels(sigs_RF_names_ordered, rotation=45, ha="right")
    ax.set_xlabel("Signature")
    ax.set_ylim(0, 1)
    ax.legend(bbox_to_anchor=(0.5, 1.15), loc="center", borderaxespad=0.0, ncol=4)

    plt.tight_layout()
    plt.savefig(
        os.path.join(fig_dir, f"r2_regional.{file_type}"), dpi=300, bbox_inches="tight"
    )


# %%
# Load the data
_df_r2_by_region = []
for cluster_num in clusters:
    print(f"Processing {cluster_num}...")
    if cluster_num == "all" or cluster_num == "avg":
        continue

    _df = load_r2(rf_dir, user_name, cluster_num, output_date, output_date_Wu)
    _df_r2_by_region.append(_df)

df_r2_by_region = pd.concat(_df_r2_by_region, axis=0)
df_r2_by_region.head()


# %% Get regional average
df_r2_by_region_avg = df_r2_by_region.groupby("sig_name").mean()
df_r2_by_region_avg["cluster_num"] = "avg"

df_r2_by_region = pd.concat([df_r2_by_region, df_r2_by_region_avg], axis=0)

# %% Join the color
df_r2_by_region["color"] = df_r2_by_region["cluster_num"].map(
    lambda x: cluster_info[x]["color"]
)
df_r2_by_region["sig_name"] = df_r2_by_region.index
df_r2_by_region.head()

# %%
plot_r2_regional(df_r2_by_region)

# %%
