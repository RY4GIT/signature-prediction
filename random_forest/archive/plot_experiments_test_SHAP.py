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
output_date = r"20250714"
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


def output_dir_name(rf_dir, user_name, output_date, cluster_num):
    output_dir = f"output_{user_name}_{output_date}_{cluster_num}"  # For regional
    return os.path.join(rf_dir, output_dir)


# %%

######################################################
# SHAP values
#####################################################


def load_shap(rf_dir, user_name, output_date, cluster_num, attrs_info):
    output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)
    _shap_df = pd.read_csv(os.path.join(output_dir, "shap_values.csv"))
    _shap_df["feature_value"] = _shap_df["feature_value"].astype(float)
    shap_df = _shap_df.merge(
        attrs_info, how="left", left_on="feature", right_on="variable_name"
    )
    return shap_df


def plot_shap(df, cluster_num, cluster_info):
    sig = "geol_weighted_ave_age_ma_copy"

    n_cols = 1
    n_rows = 1

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(5 * n_cols, 5 * n_rows),
        constrained_layout=True,
    )

    sig_data = df[df["sig_name"] == sig]

    # Order the data by the largest absolute SHAP value
    sig_data = sig_data.reindex(
        sig_data["phi"].abs().sort_values(ascending=False).index
    )

    # Determine the color based on the SHAP value
    color_dict = create_color_dict(df, "variable_name")
    colors = [color_dict[feature] for feature in sig_data["variable_name"]]

    # Color based on the directionarity of the SHAP value
    # colors = ["tab:pink" if val < 0 else "skyblue" for val in sig_data["phi"]]

    ax = axes
    # Create a horizontal bar plot
    ax.barh(
        sig_data["feature"],
        sig_data["phi"],
        xerr=sig_data["phi.var"],
        color=colors,
        edgecolor="lightgrey",
        alpha=0.7,
        ecolor="grey",  # Color of the error bars
        capsize=3,  # Add caps to the error bars
        error_kw={"alpha": 0.5},  # Increase transparency of the error bars
    )

    ax.set_xlabel("SHAP Value")
    # ax.set_ylabel("Attribute")
    ax.set_title(f"{sig}")
    ax.invert_yaxis()  # Invert y-axis to have the highest values on top

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    # fig.suptitle(f"SHAP values: {cluster_name}", fontsize=24)
    fig.subplots_adjust(top=0.9)  # Adjust the top to make space for the suptitle
    # fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(fig_dir, f"shap_{cluster_num}.{file_type}"), dpi=1200)


# CONUS-wide
df = load_shap(
    rf_dir=rf_dir,
    user_name=user_name,
    output_date=output_date,
    cluster_num="test_SHAP",
    attrs_info=attrs_info,
)
plot_shap(df=df, cluster_num="test_SHAP", cluster_info=cluster_info)

# %%

######################################################
# Attributes importance by incRMSE
#####################################################


# Function to load data
def load_data_incRMSE(rf_dir, user_name, output_date, cluster_num, attrs_info):
    output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)

    _df_imp = pd.read_csv(os.path.join(output_dir, "var_importance.csv"))

    df_imp = _df_imp.merge(
        attrs_info, how="left", left_on="predictor", right_on="variable_name"
    )

    return df_imp


# Function to plot bar plots
def plot_bar_plots(df, cluster_num, cluster_info):
    sig = "geol_weighted_ave_age_ma_copy"
    color_dict = create_color_dict(df, "variable_name")

    n_cols = 1
    n_rows = 1

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(5 * n_cols, 5 * n_rows),
        constrained_layout=True,
    )

    df_subset = df[df["sig_name"] == sig].sort_values(by="%IncMSE", ascending=False)
    sns.barplot(
        data=df_subset,
        x="%IncMSE",
        y="predictor",
        hue="predictor",
        palette=color_dict,
        ax=axes,
    )
    axes.set_xlabel("Permutation Importance (z-score)")
    # axes.set_title(sig, loc="left", fontsize=30)

    # cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    # fig.suptitle(cluster_name, fontsize=24)
    fig.subplots_adjust(top=0.9)
    fig.savefig(
        os.path.join(fig_dir, f"var_importance_bar_{cluster_num}.{file_type}"),
        dpi=1200,
    )


df_imp = load_data_incRMSE(rf_dir, user_name, output_date, "test_SHAP", attrs_info)
plot_bar_plots(df_imp, cluster_num="test_SHAP", cluster_info=cluster_info)

# %%
