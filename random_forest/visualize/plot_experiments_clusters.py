# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %%
########################## CHANGE HERE #################
output_date = r"20250312"
user_name = "raraki"
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
cluster_info = {int(k): v for k, v in cluster_plot_json.items()}
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

    # Read CONUS
    output_dir = f"{output_date}_cluster_all"
    file_path = os.path.join(rf_dir, output_dir, "r_squared.csv")
    df_conus = pd.read_csv(file_path, index_col="sig_name")
    df_conus.columns = ["CONUS-wide"]
    _dfs_r2.append(df_conus)

    # Read by cluster_num
    for cluster_num in cluster_info.keys():
        output_dir = output_dir_name(rf_dir, user_name, output_date, cluster_num)
        file_path = os.path.join(output_dir, "r_squared.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="sig_name")
            df_temp.columns = [f"{cluster_num} - {cluster_info[cluster_num]['name']}"]
            _dfs_r2.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs_r2 = pd.concat(_dfs_r2, axis=1)
    return dfs_r2, df_conus


def plot_r2_values(df, cluster_info):
    # Plotting the multiple bar plot
    colors = [
        cluster_info[cluster_num]["color"]
        for cluster_num in cluster_info.keys()
        if f"{cluster_num} - {cluster_info[cluster_num]['name']}" in df.columns
    ]
    colors.insert(0, "grey")

    fig, ax = plt.subplots(figsize=(20, 8))
    df.plot(kind="bar", color=colors, ax=ax)
    ax.set_title(r"$R^2$ for Different cluster_nums")
    ax.set_xlabel("Signature")
    ax.set_ylabel(r"$R^2$")
    ax.set_xticklabels(df.index, rotation=45, ha="right")
    ax.legend(title="cluster_nums", bbox_to_anchor=(1.05, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, "r2_per_sig.png"))


def plot_average_r2(dfs_r2, df_conus, cluster_info):
    _df_avg_r2 = dfs_r2.drop(columns="CONUS-wide").mean(axis=0).reset_index()
    _df_avg_r2.columns = ["cluster_num", "Average R-squared"]

    df_avg_r2_conus = df_conus.mean(axis=0).reset_index()
    df_avg_r2_conus.columns = ["cluster_num", "Average R-squared"]

    df_avg_r2 = pd.concat([df_avg_r2_conus, _df_avg_r2], axis=0)

    # Add colors to the DataFrame
    df_avg_r2["Color"] = df_avg_r2["cluster_num"].apply(
        lambda x: (cluster_info[x]["color"])
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        df_avg_r2["cluster_num"],
        df_avg_r2["Average R-squared"],
        color=df_avg_r2["Color"],
    )
    ax.set_title(r"Average $R^2$ for Different cluster_nums")
    ax.set_xlabel("cluster_num")
    ax.set_ylabel(r"Average $R^2$")
    ax.set_xticklabels(df_avg_r2["cluster_num"], rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, "r2_average.png"))


dfs_r2, df_conus = load_data_r2(rf_dir, user_name, output_date, cluster_info)
plot_r2_values(dfs_r2, cluster_info)
plot_average_r2(dfs_r2, df_conus, cluster_info)


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
    sigs = df["sig_name"].unique()

    n_cols = 5
    n_rows = (len(sigs) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(5 * n_cols, 5 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    for i, sig in enumerate(sigs):
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

        ax = axes[i]
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

        # ax.set_xlabel("SHAP Value")
        # ax.set_ylabel("Attribute")
        ax.set_title(f"{sig}")
        ax.invert_yaxis()  # Invert y-axis to have the highest values on top

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    cluster_name = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
    fig.suptitle(f"SHAP values: {cluster_name}", fontsize=24)
    fig.subplots_adjust(top=0.9)  # Adjust the top to make space for the suptitle
    # fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(fig_dir, f"shap_{cluster_num}.png"))


# CONUS-wide
df = load_shap(
    rf_dir=rf_dir,
    user_name=user_name,
    output_date=output_date,
    cluster_num="all",
    attrs_info=attrs_info,
)
plot_shap(df=df, cluster_num="all", cluster_info=cluster_info)

# By clusters
for cluster_num in cluster_info.keys():
    print(f"Processing {cluster_num}...")
    df = load_shap(
        rf_dir=rf_dir,
        user_name=user_name,
        output_date=output_date,
        cluster_num=cluster_num,
        attrs_info=attrs_info,
    )
    plot_shap(df=df, cluster_num=cluster_num, cluster_info=cluster_info)
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
    fig.savefig(os.path.join(fig_dir, f"var_importance_bar_{cluster_num}.png"))


# Main function to loop through cluster_nums
for cluster_num in clusters:
    print(f"Processing {cluster_num}...")

    df_imp = load_data_incRMSE(rf_dir, user_name, output_date, cluster_num, attrs_info)
    plot_bar_plots(df_imp, cluster_num=cluster_num, cluster_info=cluster_info)


# %%


######################################################
# Compare predicted vs observed signatures
#####################################################


def load_data_sigpred(output_date, rf_dir, cluster_info):
    _dfs = []

    # Read CONUS
    output_dir = f"{output_date}_caravan_us"
    file_path = os.path.join(rf_dir, output_dir, "predicted_signatures.csv")
    df_conus = pd.read_csv(file_path, index_col="gauge_id")
    df_conus["region"] = "CONUS-wide"
    _dfs.append(df_conus)

    # Read by cluster_num
    for cluster_num in cluster_info.keys():
        output_dir = f"{output_date}_cluster_num_{cluster_num}"
        file_path = os.path.join(rf_dir, output_dir, "predicted_signatures.csv")
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path, index_col="gauge_id")
            df_temp["region"] = f"{cluster_num} - {cluster_info[cluster_num]['name']}"
            _dfs.append(df_temp)
        else:
            print(f"File not found: {file_path}")

    dfs = pd.concat(_dfs, axis=0)
    return dfs, df_conus


df_sigpred, df_conus = load_data_sigpred(output_date, rf_dir, cluster_info)
# %%__________________________________________________________________________________
# LOAD OBSERVED AND PREDICTED SIGNAUTURES

# Concat original signature file that is used by sig_name and gauge_id
# file_path = os.path.join(rf_dir, f"{output_date}_caravan_us", "config.yaml")
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
eco_camels_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\cluster_nums\cluster_num_camels.csv"
eco_hysets_file = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\cluster_nums\cluster_num_hysets.csv"
eco_camels = pd.read_csv(eco_camels_file, index_col="gauge_id")
eco_hysets = pd.read_csv(eco_hysets_file, index_col="gauge_id")
eco_caravan = pd.concat([eco_camels, eco_hysets])
df_sigs_eco = df_sigs.join(eco_caravan, how="left")


# %% ______________________________________________________________________________________
# Plot the residuals R2 by cluster_num or CONUS-wide
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
# # plot_sigerr_map(df_sigs, "TotalRR", cluster_num_overlay)
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

    sample_counts = df["cluster_num"].value_counts()
    valid_cluster_nums = sample_counts[sample_counts >= 100].index
    df_filt = df[df["cluster_num"].isin(valid_cluster_nums)].copy()
    df_filt["cluster_numumber"] = (
        df_filt["cluster_num"].str.extract(r"(\d+)").astype(int)
    )

    custom_order = {
        "11": 0,
        "1210": 1,
        "6713": 2,
        "81": 3,
        "82": 4,
        "91": 5,
        "92": 6,
    }
    df_filt["custom_order"] = df_filt["cluster_numumber"].map(custom_order)

    # Sort by the custom order
    df_sorted = df_filt.sort_values("custom_order")
    df_sorted = df_sorted.drop(columns=["custom_order"])
    # df_sorted = df_filt.sort_values("cluster_numumber")

    # Plot the boxplot using Seaborn
    cluster_num_colors = [
        "#D1E8BA",  # MEDITERRANEAN CALIFORNIA (11)
        "#FFDB71",  # WESTERN DESERTS (1210)
        "#5DC05A",  # WESTERN FORESTED MOUNTAINS (6713)
        "#BBDD90",  # NORTH EASTERN FORESTS (81)
        "#4DCAC2",  # SOUTH EASTERN FORESTS (82)
        "#BD9977",  # NORTH GREAT PLAINS (91)
        "#FECE9F",  # SOUTH GREAT PLAINS (92)
    ]

    # cluster_num_colors = [
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
        y="cluster_num",
        data=df_sorted,
        palette=cluster_num_colors,
        order=df_sorted["cluster_num"].unique(),
    )

    # Customize the plot
    boxplot.set_xlabel(r"$|pred-obs|/obs$" + f"{plot_config['unit']}")
    boxplot.set_ylabel("cluster_num")
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

# # Function to plot pie charts
# def plot_pie_charts(
#     df,
#     cluster_num,
#     cluster_info,
#     attrs_colors,
# ):
#     sigs = df["sig_name"].unique()

#     n_cols = 4
#     n_rows = (len(sigs) + n_cols - 1) // n_cols

#     fig, axes = plt.subplots(
#         nrows=n_rows,
#         ncols=n_cols,
#         figsize=(8 * n_cols, 10 * n_rows),
#         constrained_layout=True,
#     )
#     axes = axes.flatten()

#     for i, sig in enumerate(sigs):
#         try:
#             df_subset = df[df["sig_name"] == sig]
#             grouped = df_subset.groupby("Group")["%IncMSE"].sum()
#             total = grouped.sum()
#             normalized = grouped / total

#             axes[i].pie(
#                 normalized,
#                 labels=normalized.index,
#                 colors=[attrs_info[group] for group in normalized.index],
#             )
#             axes[i].set_title(sig, loc="left", fontsize=30)

#         except Exception as e:
#             print(f"Error plotting pie chart for {sig}: {e}")
#             axes[i].set_title(sig, loc="left", fontsize=30)
#             continue

#     for j in range(i + 1, len(axes)):
#         axes[j].set_visible(False)

#     fig.suptitle(cluster_name, fontsize=32)
#     fig.savefig(os.path.join(fig_dir, f"var_importance_pie_{cluster_num}.png"))

#     return axes


# __________________________________________________________
# Conus- wide
# cluster_num = "caravan_us"
# cluster_name = "CONUS-wide"
# print(f"Processing {cluster_name}...")
# df_imp_conus = load_data_incRMSE(
# )
# sigs = df_imp_conus["sig_name"].unique()

# plot_bar_plots(df_imp_conus, sigs, cluster_num, cluster_name)
# plot_pie_charts(df_imp_conus, sigs, attrs_colors, cluster_name, cluster_name)
