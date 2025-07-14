# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import yaml
import geopandas as gpd

# %%
########################## CHANGE HERE #################
output_date = r"output_20240723"
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


fig_dir = os.path.join(out_dir_rf, f"{output_date}_figures")
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)


# %%
def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


ecoregion_info = read_json_file(
    r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize\plot_config_ecoregion_colors_v1.json"
)
ecoregion_info = {int(k): v for k, v in ecoregion_info.items()}
ecoregion_numbers = ecoregion_info.keys()

attrs_colors = read_json_file("plot_config_attrs_colors.json")

_ecoregion_overlay = gpd.read_file(
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\EcoRegions\NA_CEC_Eco_Level1.shp"  # NA_CEC_Eco_Level1
)
_ecoregion_overlay = _ecoregion_overlay.set_crs(_ecoregion_overlay.crs)
ecoregion_overlay = _ecoregion_overlay.to_crs("epsg:4326")
# %%

######################################################
# R-squares comparison by region
#####################################################


def load_data_r2(output_date, out_dir_rf, ecoregion_info, ecoregion_numbers):
    _dfs_r2 = []

    # Read CONUS
    output_dir = f"{output_date}_caravan_us"
    file_path = os.path.join(out_dir_rf, output_dir, "r_squared.csv")
    df_conus = pd.read_csv(file_path, index_col="sig_name")
    df_conus.columns = [f"CONUS-wide"]
    _dfs_r2.append(df_conus)

    # Read by ecoregion
    for ecoregion_n in ecoregion_numbers:
        output_dir = f"{output_date}_ecoregion_{ecoregion_n}"
        file_path = os.path.join(out_dir_rf, output_dir, "r_squared.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="sig_name")
            df_temp.columns = [f'{ecoregion_n} - {ecoregion_info[ecoregion_n]["name"]}']
            _dfs_r2.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs_r2 = pd.concat(_dfs_r2, axis=1)
    return dfs_r2, df_conus


def plot_r2_values(df, ecoregion_info, ecoregion_numbers):
    # Plotting the multiple bar plot
    colors = [
        ecoregion_info[ecoregion]["color"]
        for ecoregion in ecoregion_numbers
        if f'{ecoregion} - {ecoregion_info[ecoregion]["name"]}' in df.columns
    ]
    colors.insert(0, "grey")

    fig, ax = plt.subplots(figsize=(20, 8))
    df.plot(kind="bar", color=colors, ax=ax)
    ax.set_title(r"$R^2$ for Different Ecoregions")
    ax.set_xlabel("Signature")
    ax.set_ylabel(r"$R^2$")
    ax.set_xticklabels(df.index, rotation=45, ha="right")
    ax.legend(title="Ecoregions", bbox_to_anchor=(1.05, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, f"r2_per_sig.png"))


def plot_average_r2(dfs_r2, df_conus, ecoregion_info):
    _df_avg_r2 = dfs_r2.drop(columns="CONUS-wide").mean(axis=0).reset_index()
    _df_avg_r2.columns = ["Ecoregion", "Average R-squared"]

    df_avg_r2_conus = df_conus.mean(axis=0).reset_index()
    df_avg_r2_conus.columns = ["Ecoregion", "Average R-squared"]

    df_avg_r2 = pd.concat([df_avg_r2_conus, _df_avg_r2], axis=0)

    # Add colors to the DataFrame
    df_avg_r2["Color"] = df_avg_r2["Ecoregion"].apply(
        lambda x: (
            ecoregion_info[int(x.split(" - ")[0])]["color"] if " - " in x else "grey"
        )
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        df_avg_r2["Ecoregion"], df_avg_r2["Average R-squared"], color=df_avg_r2["Color"]
    )
    ax.set_title(r"Average $R^2$ for Different Ecoregions")
    ax.set_xlabel("Ecoregion")
    ax.set_ylabel(r"Average $R^2$")
    ax.set_xticklabels(df_avg_r2["Ecoregion"], rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, f"r2_average.png"))

    print(df_avg_r2)


dfs_r2, df_conus = load_data_r2(
    output_date, out_dir_rf, ecoregion_info, ecoregion_numbers
)
plot_r2_values(dfs_r2, ecoregion_info, ecoregion_numbers)
plot_average_r2(dfs_r2, df_conus, ecoregion_info)


# %%
dfs_r2
# %%


# %%
# # %%#
# # ____________________________________________________________________________________
# ######################################################
# # Attributes importance by ecoregion
# #####################################################


# Function to load data
def load_data_incRMSE(out_dir_rf, output_date, ecoregion_n, plot_config_path):
    if not isinstance(ecoregion_n, (int, float)):
        output_dir = f"{output_date}_{ecoregion_n}"
    else:
        output_dir = f"{output_date}_ecoregion_{ecoregion_n}"

    _df_imp = pd.read_csv(os.path.join(out_dir_rf, output_dir, "var_importance.csv"))
    df_plot_config = pd.read_csv(plot_config_path)
    df_imp = _df_imp.merge(
        df_plot_config, how="left", left_on="predictor", right_on="variable_name"
    )

    return df_imp


# Function to map colors
def map_colors(group):
    return attrs_colors.get(group, "lightgrey")


# Function to create color dictionary
def create_color_dict(df_imp):
    df_imp["color"] = df_imp["Group"].apply(map_colors)
    return df_imp.set_index("variable_name")["color"].to_dict()


# Function to plot bar plots
def plot_bar_plots(df, sigs, ecoregion_n, ecoregion_name):

    color_dict = create_color_dict(df)

    n_cols = 4
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

    fig.suptitle(ecoregion_name, fontsize=32)
    fig.savefig(os.path.join(fig_dir, f"var_importance_bar_{ecoregion_n}.png"))


# %%

# __________________________________________________________
# Conus- wide
ecoregion_n = "caravan_us"
ecoregion_name = "CONUS-wide"
print(f"Processing {ecoregion_name}...")
df_imp_conus = load_data_incRMSE(
    out_dir_rf, output_date, ecoregion_n, plot_attrs_config_path
)
sigs = df_imp_conus["sig_name"].unique()

plot_bar_plots(df_imp_conus, sigs, ecoregion_n, ecoregion_name)
