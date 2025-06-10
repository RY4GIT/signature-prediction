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
    r"C:\Users\flipl\dev\signature-prediction\plotting\HydroML\plot_config_expcolors_subset.json"
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
    fig, ax = plt.subplots(figsize=(7, 6))
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

    fig, ax = plt.subplots(figsize=(4, 6))
    ax.bar(df_avg_r2["Exp"], df_avg_r2["Average R-squared"], color=df_avg_r2["Color"])
    ax.set_title(r"Average $R^2$ for Different Experiments")
    ax.set_xlabel("Exp")
    ax.set_ylabel(r"Average $R^2$")
    ax.set_xticklabels(df_avg_r2["Exp"], rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, f"r2_average.png"))


dfs_r2 = load_data_r2(output_date, out_dir_rf, exp_info, exp_types, experiment_name)
selected_rows = [
    "TotalRR",
    "AverageStorage",
    "BFI",
    "BaseflowRecessionK",
    "IE_thresh",
    "SE_thresh",
]
dfs_r2 = dfs_r2.loc[selected_rows].copy()
plot_r2_values(dfs_r2, exp_info, exp_types)
plot_average_r2(dfs_r2, exp_info)
# %%


# %%
# ____________________________________________________________________________________
######################################################
# Attributes importance by ecoregion
#####################################################


# Function to load data
def load_data_incRMSE(
    out_dir_rf, output_date, exp_info, experiment_name, plot_config_path
):
    output_dir = f"{output_date}_{experiment_name}_{exp_info['shortname']}"

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
def plot_bar_plots(df, sigs, exp_info, exp_name):
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

    fig.suptitle(exp_name, fontsize=32)
    fig.savefig(
        os.path.join(fig_dir, f"var_importance_bar_{exp_info['shortname']}.png")
    )


# Function to plot pie charts
def plot_pie_charts(df, sigs, color_mapping, exp_info, exp_name):
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
        try:
            df_subset = df[df["sig_name"] == sig]
            grouped = df_subset.groupby("Group")["%IncMSE"].sum()
            total = grouped.sum()
            normalized = grouped / total

            axes[i].pie(
                normalized,
                labels=normalized.index,
                colors=[color_mapping[group] for group in normalized.index],
            )
            axes[i].set_title(sig, loc="left", fontsize=30)

        except Exception as e:
            print(f"Error plotting pie chart for {sig}: {e}")
            axes[i].set_title(sig, loc="left", fontsize=30)
            continue

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(exp_name, fontsize=32)
    fig.savefig(
        os.path.join(fig_dir, f"var_importance_pie_{exp_info['shortname']}.png")
    )

    return axes


# %%
# ____________________________________________________________
# Per Experiment

# Main function to loop through # Per Experiment

for exp_n in exp_types:
    exp_case = f"{exp_n} - {exp_info[exp_n]['name']}"
    print(f"Processing {exp_case}...")

    df_imp = load_data_incRMSE(
        out_dir_rf,
        output_date,
        exp_info[exp_n],
        experiment_name,
        plot_attrs_config_path,
    )
    plot_bar_plots(df_imp, sigs, exp_info[exp_n], exp_case)
    plot_pie_charts(df_imp, sigs, attrs_colors, exp_info[exp_n], exp_case)


# %%___________________________________________________________________________________
# Compare predicted vs observed signatures
exp_info
# %%


def load_data_sigpred(output_date, out_dir_rf, exp_info, exp_types):
    _dfs = []

    # Read by gages 2experiment
    for exp_n in exp_types:
        exp_shortname = exp_info[exp_n]["shortname"]
        output_dir = f"{output_date}_{experiment_name}_{exp_shortname}"
        file_path = os.path.join(out_dir_rf, output_dir, "predicted_signatures.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="gauge_id")
            df_temp["region"] = f"{exp_n} - {exp_info[exp_n]['name']}"
            _dfs.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs = pd.concat(_dfs, axis=0)
    return dfs


df_sigpred = load_data_sigpred(output_date, out_dir_rf, exp_info, exp_types)

# %%
# Check the sample size of RF experiment based on the signature data file
# Used in the config

for exp_n in exp_types:
    # Get some info
    exp_shortname = exp_info[exp_n]["shortname"]
    exp_longname = exp_info[exp_n]["name"]
    output_dir = f"{output_date}_{experiment_name}_{exp_shortname}"

    # Read the YAML config file
    config_file = os.path.join(out_dir_rf, output_dir, "config.yaml")

    with open(config_file, "r") as file:
        config_exp = yaml.safe_load(file)
        print(config_exp["paths"]["train"]["signatures"])

    # Read the signature file
    sig_file = out_dir + config_exp["paths"]["train"]["signatures"]
    sig_obs_df = pd.read_csv(sig_file)

    # Count the data
    print(f"{exp_n} - {exp_longname}")
    print(f"Signature sample   : {len(sig_obs_df)}")
    print(
        f"IE Signature sample: {len(sig_obs_df) - sig_obs_df['IE_thresh'].isna().sum()}"
    )
    print("\n")

# %%__________________________________________________________________________________
# LOAD OBSERVED AND PREDICTED SIGNAUTURES

# Concat original signature file that is used by sig_name and gauge_id
# file_path = os.path.join(out_dir_rf, f"{output_date}_caravan_us", "config.yaml")
# with open(file_path, "r") as file:
#     rf_config = yaml.safe_load(file)

# sigobs_path = rf_config["paths"]["train"]["signatures"]
# if sigobs_path.startswith("/"):
#     sigobs_path = sigobs_path.lstrip("/")
sigobs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20240609_tunedparams\out_calc_All_custom_filt.csv"

# Load the observed signatures
df_sigobs = pd.read_csv(sigobs_path)

# Subset df_sigpred based on region
df_sigpred_conus = df_sigpred[df_sigpred["region"] == "CONUS-wide"]
df_sigpred_regional = df_sigpred[df_sigpred["region"] != "CONUS-wide"]

# Pivot df_sigpred_regional to make each signature a column
df_sigpred_pivot = (
    df_sigpred_conus.reset_index()
    .pivot(index="gauge_id", columns="sig_name", values="prediction")
    .reset_index()
)

# Ensure gauge_id columns are strings and strip any leading/trailing whitespace
df_sigobs["gauge_id"] = df_sigobs["gauge_id"].astype(str).str.strip()
df_sigpred_pivot["gauge_id"] = df_sigpred_pivot["gauge_id"].astype(str).str.strip()

# Merge the pivoted df_sigpred with df_sigobs on gauge_id
df_merged = pd.merge(
    df_sigobs, df_sigpred_pivot, on="gauge_id", how="left", suffixes=("", "_pred")
)
df_merged.set_index("gauge_id", inplace=True)

# %%
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
caravan_attrs = pd.concat([attrs_camels, attrs_hysets])

# %%
# Merge attributes with the merged signatures DataFrame
df_sigs = pd.merge(caravan_attrs, df_merged, on="gauge_id", how="left")

# Save the final DataFrame to a CSV file
file_path = os.path.join(fig_dir, "predicted_signatures_merged.csv")
df_sigs.to_csv(file_path)
# %%
eco_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\EcoRegions\Ecoregion_camels.csv"
eco_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\EcoRegions\Ecoregion_hysets.csv"
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])
df_sigs_eco = df_sigs.join(eco_caravan, how="left")


# %% ______________________________________________________________________________________
# Plot the residuals R2 by ecoregion or CONUS-wide
def plot_sigerr_map(df, sig_name, overlay_layer):
    # Get plot config
    plot_config = plot_sigs_config.loc[
        plot_sigs_config["column_name"] == sig_name
    ].iloc[0]

    # Calculate abs diffrences
    frac_err = abs(df[sig_name] - df[sig_name + "_pred"]) / df[sig_name]
    # abs_err = df[sig_name] - df[sig_name + "_pred"]

    # Set up the map
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    # Add a legend
    overlay_layer.plot(
        ax=ax,
        edgecolor="black",
        facecolor="none",
        linewidth=0.5,
        aspect=1.1,
        zorder=100,
    )

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="lightgrey",  # Set land color to light gray
    )
    ax.add_feature(land)

    # Set extent to CONUS
    ax.set_extent([-125.5, -66.95, 24.396308, 47.5])
    # Add map features
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")

    # Plotting the filtered data
    scatter = ax.scatter(
        df["gauge_lon_x"],
        df["gauge_lat_x"],
        c=frac_err,
        cmap="Reds",
        marker="o",
        # edgecolors="grey",
        s=5,
        alpha=0.8,
        zorder=99,
        vmin=0,
        vmax=frac_err.quantile(0.90),
    )

    # for geometry in overlay_layer.geometry:
    #     ax.add_geometries([geometry], crs=ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=1, zorder=100)

    ax.set_title(f"{plot_config['label']}")

    # Adding a colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
    cbar.set_label(
        r"$|pred-obs|/obs$" + f"{plot_config['unit']}", rotation=270, labelpad=30
    )
    # cbar.set_label(r"$|e|$" + f'{plot_config["unit"]}', rotation=270, labelpad=30)
    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"sigerr_{sig_name}.png"))


# %%
for sigs_name in plot_sigs_config.column_name:
    try:
        plot_sigerr_map(df_sigs, sigs_name)
    except:
        print(f"{sigs_name} is not in the prediction")
# # %%
# df_sigs.columns
# # plot_sigerr_map(df_sigs, "TotalRR", ecoregion_overlay)
# #
# %%
# ______________________________________________________________
# Get the error bar plot per region


def plot_err_box(df, sig_name):
    plot_config = plot_sigs_config.loc[
        plot_sigs_config["column_name"] == sig_name
    ].iloc[0]

    # Calculate fractional error
    df["frac_err"] = abs(df[sig_name] - df[sig_name + "_pred"]) / df[sig_name]

    # Calculate the 99th percentile of the fractional error
    upper_lim = df["frac_err"].quantile(0.99)

    # df["abs_err"] = abs(df[sig_name] - df[sig_name + "_pred"])
    # abs_err_percentile = df["abs_err"].quantile(0.99)

    sample_counts = df["ecoregion"].value_counts()
    valid_ecoregions = sample_counts[sample_counts >= 100].index
    df_filt = df[df["ecoregion"].isin(valid_ecoregions)].copy()
    df_filt["exp_number"] = df_filt["ecoregion"].str.extract(r"(\d+)").astype(int)

    custom_order = {
        "11": 0,
        "1210": 1,
        "6713": 2,
        "81": 3,
        "82": 4,
        "91": 5,
        "92": 6,
    }
    df_filt["custom_order"] = df_filt["exp_number"].map(custom_order)

    # Sort by the custom order
    df_sorted = df_filt.sort_values("custom_order")
    df_sorted = df_sorted.drop(columns=["custom_order"])
    # df_sorted = df_filt.sort_values("exp_number")

    # Plot the boxplot using Seaborn
    ecoregion_colors = [
        "#D1E8BA",  # MEDITERRANEAN CALIFORNIA (11)
        "#FFDB71",  # WESTERN DESERTS (1210)
        "#5DC05A",  # WESTERN FORESTED MOUNTAINS (6713)
        "#BBDD90",  # NORTH EASTERN FORESTS (81)
        "#4DCAC2",  # SOUTH EASTERN FORESTS (82)
        "#BD9977",  # NORTH GREAT PLAINS (91)
        "#FECE9F",  # SOUTH GREAT PLAINS (92)
    ]

    # ecoregion_colors = [
    #     "#9ACDCF",
    #     "#5DC05A",
    #     "#4DCAC2",
    #     "#BBDD90",
    #     "#FECE9F",
    #     "#FFDB71",
    #     "#D1E8BA",
    #     "#BBDD90",
    # ]

    plt.figure(figsize=(12, 5))
    boxplot = sns.boxplot(
        x="frac_err",
        y="ecoregion",
        data=df_sorted,
        palette=ecoregion_colors,
        order=df_sorted["ecoregion"].unique(),
    )

    # Customize the plot
    boxplot.set_xlabel(r"$|pred-obs|/obs$" + f"{plot_config['unit']}")
    boxplot.set_ylabel("Ecoregion")
    boxplot.set_title(f"{plot_config['label']}")
    boxplot.set_xlim([0, upper_lim])

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"sigerrbox_{sig_name}.png"))
    plt.show()


for sigs_name in plot_sigs_config.column_name:
    try:
        plot_err_box(df_sigs_eco, sigs_name)
    except Exception as e:
        print(f"An error occurred: {e}")

# %%
