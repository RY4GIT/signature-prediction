# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import yaml

# %%
########################## CHANGE HERE #################
output_date = r"output_raraki_20250517"
experiment_name = "subset"
########################################################

# ____________________________________________________________________________________
# Config
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out"
out_dir_rf = os.path.join(out_dir, "rf")
plot_attrs_config_path = "plot_config_attrs_info.csv"
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\signatures\visualize\plot_sigs_config.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)
caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
attrs_camels_file = os.path.join(
    caravan_attrs_dir,
    "camels",
    f"attributes_other_camels.csv",
)
attrs_hysets_file = os.path.join(
    caravan_attrs_dir,
    "hysets",
    f"attributes_other_hysets.csv",
)


fig_dir = os.path.join(out_dir_rf, f"{output_date}_{experiment_name}_figures")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


exp_info = read_json_file(
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\plot_config_expcolors_subset.json"
)
exp_info = {int(k): v for k, v in exp_info.items()}
exp_types = exp_info.keys()

attrs_colors = read_json_file("plot_config_attrs_colors.json")

sigs_config = pd.read_csv(
    r"C:\Users\flipl\dev\signature-prediction\signatures\visualize\plot_sigs_config.csv"
)
sigs = sigs_config.column_name
exp_info
# %%
######################################################
# R-squares comparison by region
#####################################################


def load_data_r2(output_date, out_dir_rf, exp_info, exp_types, experiment_name):
    _dfs_r2 = []

    # Read by ecoregion
    for exp_n in exp_types:
        exp_shortname = exp_info[exp_n]["shortname"]
        output_dir = f"{output_date}_{exp_shortname}"
        # output_dir = f"{output_date}_{experiment_name}_{exp_shortname}"
        file_path = os.path.join(out_dir_rf, output_dir, "r_squared.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="sig_name")
            df_temp.columns = [f"{exp_n} - {exp_info[exp_n]['name']}"]
            _dfs_r2.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs_r2 = pd.concat(_dfs_r2, axis=1)
    return dfs_r2


def plot_r2_values(df, exp_info, exp_type):
    # Plotting the multiple bar plot
    colors = [
        exp_info[exp_type]["color"]
        for exp_type in exp_types
        if f"{exp_type} - {exp_info[exp_type]['name']}" in df.columns
    ]
    # colors.insert(0, "grey")
    # Create labels for the columns that exist in the dataframe
    labels = [exp_info[i]["name"] for i in exp_info.keys()]

    # fig, ax = plt.subplots(figsize=(18, 6))
    # Set fontsize for this plot
    plt.rcParams.update({"font.size": 16})
    fig, ax = plt.subplots(figsize=(12, 7.5))
    df.plot(kind="bar", color=colors, ax=ax)
    ax.legend(labels, fontsize=12)
    # ax.set_title(r"$R^2$ for Different Experiments")
    ax.set_xlabel("Signature")
    ax.set_ylabel(r"$R^2$")
    ax.set_xticklabels(df.index, rotation=45, ha="right")
    # ax.legend()
    ax.set_ylim(-0.1, 1.1)
    # ax.legend(title="Experiment", bbox_to_anchor=(1.05, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, f"r2_per_sig.png"), dpi=300)


def plot_average_r2(dfs_r2, exp_info):
    df_avg_r2 = dfs_r2.mean(axis=0).reset_index()
    df_avg_r2.columns = ["Exp", "Average R-squared"]

    # Add colors to the DataFrame
    df_avg_r2["Color"] = df_avg_r2["Exp"].apply(
        lambda x: (exp_info[int(x.split(" - ")[0])]["color"] if " - " in x else "grey")
    )

    fig, ax = plt.subplots(figsize=(5, 6))
    ax.bar(df_avg_r2["Exp"], df_avg_r2["Average R-squared"], color=df_avg_r2["Color"])
    ax.set_title(r"Average $R^2$ for Different Experiments")
    ax.set_xlabel("Exp")
    ax.set_ylabel(r"Average $R^2$")
    ax.set_xticklabels(df_avg_r2["Exp"], rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, f"r2_average.png"))


dfs_r2 = load_data_r2(output_date, out_dir_rf, exp_info, exp_types, experiment_name)
selected_rows = [
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
dfs_r2 = dfs_r2.loc[selected_rows].copy()
plot_r2_values(dfs_r2, exp_info, exp_types)
plot_average_r2(dfs_r2, exp_info)
# %%
