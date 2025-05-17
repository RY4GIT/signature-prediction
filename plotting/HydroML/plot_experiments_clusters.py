# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

# %%
########################## CHANGE HERE #################
output_date = r"20250430"
user_name = "raraki"
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

# ____________________________________________________________________________________
# I/O paths

# Current director
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

# Output directory of the random forest results
rf_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf"
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

# Cluster colors
with open("plot_config_expcolors_clusters.json", "r") as file:
    cluster_plot_json = json.load(file)
# Convert keys to integers except for the first item
cluster_info = {int(k) if k.isdigit() else k: v for k, v in cluster_plot_json.items()}
clusters = cluster_info.keys()
print(clusters)


# ____________________________________________________________________________________
# Attributes
caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
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


def output_dir_name(rf_dir, user_name, output_date, cluster_num):
    if not isinstance(cluster_num, (int, float)):
        output_dir = (
            f"output_{user_name}_{output_date}_cluster_{cluster_num}"  # For regional
        )
    else:
        output_dir = f"output_{user_name}_{output_date}_cluster_{cluster_num}"
    return os.path.join(rf_dir, output_dir)


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


def plot_r2_values(df, cluster_info):
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


def plot_average_r2(dfs_r2, cluster_info):
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
    df_avg_r2.to_csv(os.path.join(fig_dir, f"r2_average.csv"), index=True)


dfs_r2 = load_data_r2(rf_dir, user_name, output_date, cluster_info)
plot_r2_values(dfs_r2, cluster_info)
plot_average_r2(dfs_r2, cluster_info)
