# %% Plot signatures from multiple sources (Caravan, GAGES-II, RF predictions)
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings


# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
print("Loading config...")

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\signatures\visualize")

# Google Drive directory
gdrive_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"

# Local directory (For Caravan data)
local_dir = r"D:\data"

# Output directory (For signatures results, change name to match the current run dates)
out_dir = os.path.join(gdrive_dir, "out", "signatures", "caravan_us_20250525")
out_dir_gages2 = os.path.join(gdrive_dir, "out", "signatures", "gages2_20250608")
rf_out_dir = os.path.join(gdrive_dir, "out", "rf", "output_raraki_20250826_cluster_all")
fig_dir = os.path.join(
    gdrive_dir,
    "figs",
)

# Make Figure directory
if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# Plotting config
plot_sigs_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\figures\HESS25\plot_sigs_config.csv"
)
plot_sigs_config = pd.read_csv(plot_sigs_config_path)

# Drop Wu signatures from the plot_sigs_config
plot_sigs_config = plot_sigs_config[
    ~plot_sigs_config["column_name"].isin(
        ["R_Pint_RC", "R_Pvol_RC", "diff_RCPint_RCPvol"]
    )
]

# Conus extent
conus_extent = [-125.5, -66.95, 24.396308, 47.5]

# %%
# ____________________________________________________________________________________
# Load data
print("Loading attributes data...")

caravan_attrs_dir = os.path.join(local_dir, "Caravan1.5", "attributes")
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
attrs_camels = pd.read_csv(attrs_camels_file, index_col="gauge_id")
attrs_hysets = pd.read_csv(attrs_hysets_file, index_col="gauge_id")
attrs_caravan = pd.concat([attrs_camels, attrs_hysets])


# %% #######################################################
# Loading the data
############################################################
print("Loading signatures results file ...")

print("Loading signatures results file for Caravan ...")
_df_sigs_cara = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area.csv"),
    index_col="gauge_id",
)
_df_sigs_cara["source"] = "Caravan_obs"
_df_sigs_cara["order"] = 1

print("Loading signatures results file for GAGES2 ...")
_df_sigs_gages2 = pd.read_csv(
    os.path.join(out_dir_gages2, "out_calc_All_custom_filt_qc_snow.csv"),
)
_df_sigs_gages2["gauge_id"] = "gages2_" + _df_sigs_gages2["gauge_id"].astype(
    str
).str.zfill(8)
_df_sigs_gages2.set_index("gauge_id", inplace=True)
_df_sigs_gages2["source"] = "GAGES2_obs"
_df_sigs_gages2["order"] = 2

print("Loading signatures results from RF predictions (overlap, baddata basins)...")
_df_sigs_rf_overlap_baddata = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_gg2_baddata.csv"),
    index_col="gauge_id",
)
# Pivot the dataframe to make signature names into columns
_df_sigs_rf_overlap_baddata = _df_sigs_rf_overlap_baddata.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_overlap_baddata["source"] = "RF_overlap_baddata"
_df_sigs_rf_overlap_baddata["order"] = 3

print("Loading signatures results from RF predictions (only hys basins)...")
_df_sigs_rf_hys_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_hys_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_hys_only = _df_sigs_rf_hys_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_hys_only["source"] = "RF_hys_only"
_df_sigs_rf_hys_only["order"] = 4

print("Loading signatures results from RF predictions (only GAGES2 basins)...")
_df_sigs_rf_gg2_only = pd.read_csv(
    os.path.join(rf_out_dir, "predicted_signatures_pred_gg2_only.csv"),
    index_col="gauge_id",
)
_df_sigs_rf_gg2_only = _df_sigs_rf_gg2_only.pivot(
    columns="sig_name", values="prediction"
)
_df_sigs_rf_gg2_only["source"] = "RF_gg2_only"
_df_sigs_rf_gg2_only["order"] = 5

# %%
print("Concatenating signatures results...")
_df_sigs = pd.concat(
    [
        _df_sigs_cara,
        _df_sigs_gages2,
        _df_sigs_rf_overlap_baddata,
        _df_sigs_rf_hys_only,
        _df_sigs_rf_gg2_only,
    ]
)
df_sigs = _df_sigs.drop(
    columns=["gauge_name", "country", "gauge_lat", "gauge_lon", "area"]
).join(attrs_caravan, how="left")
df_sigs.to_csv(os.path.join(rf_out_dir, "sigs_predicted_observed_joined.csv"))


# %%
#######################################################
# Preprocess the data
#######################################################

# Calcaulte some signatures
# df_sigs["diff_RCPint_RCPvol"] = df_sigs["R_Pint_RC"] - df_sigs["R_Pvol_RC"]
df_sigs["diff_IE_SE_thresh"] = df_sigs["IE_thresh"] - df_sigs["SE_thresh"]
df_sigs["diff_IE_Str_thresh"] = df_sigs["IE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["diff_SE_Str_thresh"] = df_sigs["SE_thresh"] - df_sigs["Storage_thresh"]
df_sigs["avg_IE_SE_thresh"] = (df_sigs["IE_thresh"] + df_sigs["SE_thresh"]) / 2
df_sigs["avg_IE_SE_signif"] = (
    df_sigs["IE_thresh_signif"] + df_sigs["SE_thresh_signif"]
) / 2
df_sigs["avg_IE_SE_thresh"].iloc[df_sigs["avg_IE_SE_thresh"] > 300] = np.nan
# %%
# Mask out gauges with high snow
frac_snow_thresh = 0.2
low_snow = (
    (df_sigs["SNOW_PCT_PRECIP"] < frac_snow_thresh * 100)
    | (df_sigs["SNOW_PCT_PRECIP"].isna())
) | ((df_sigs["SNOWICENLCD06"] < frac_snow_thresh) | (df_sigs["SNOWICENLCD06"].isna()))
mask_cols = [
    "IE_thresh",
    "SE_thresh",
    "Storage_thresh",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "Storage_thresh_signif",
]
df_sigs[mask_cols] = df_sigs[mask_cols].mask(~low_snow)
# This line replaces values with NaN for any rows where low_snow is False
# low_snow is True for gauges with snow < threshold, False otherwise
# So ~low_snow is True for gauges with high snow, which get masked to NaN

print(
    f"{df_sigs['IE_thresh'].isna().sum()} gauges ({df_sigs['IE_thresh'].isna().sum() / len(df_sigs) * 100:.1f}%) have snow data above {frac_snow_thresh * 100}%"
)
# %%
print("Data length: ", len(df_sigs))
print("Baseflow data length: ", len(df_sigs[df_sigs["BFI"].notna()]))
print("Overlandflow data length: ", len(df_sigs[df_sigs["IE_thresh"].notna()]))


# %%
# Get the percentile
def below_thresh_percentile(column_data, thresh_value):
    new_percentile = column_data.apply(
        lambda x: 0 if x > thresh_value else (1 - (x / thresh_value)) * 100
    )
    return new_percentile


for sigs_name in plot_sigs_config["column_name"]:
    column_data = df_sigs[sigs_name]

    # Calculate the percentile rank for each value in the column
    if "_signif" in sigs_name:
        df_sigs[sigs_name + "_perc"] = below_thresh_percentile(df_sigs[sigs_name], 0.05)
    else:
        df_sigs[sigs_name + "_perc"] = column_data.rank(pct=True) * 100


# %% ######################
# PLOTTING FUNCTIONS
##########################

# %% ######################
#
#  Plot signature value histogram
#
##########################


def plot_sig_hist(df, sig_name, fig_dir=None):
    fig = plt.figure(figsize=(3, 1.5))  # Made figure taller to accommodate colorbar
    fontsize = 14
    ax = fig.add_subplot(1, 1, 1, facecolor="white")

    x_data = df[sig_name].dropna()
    x_data = x_data[~np.isinf(x_data)]

    # Plot KDE instead of histogram
    x_data.plot.kde(ax=ax, color="tab:blue", linewidth=3, label=None)

    # Add x line at 0.25, 0.5, 0.75
    ax.axvline(
        x_data.quantile(0.25), color="tab:blue", linestyle="--", alpha=0.3, linewidth=2
    )
    ax.axvline(
        x_data.quantile(0.5), color="tab:blue", linestyle="--", alpha=0.3, linewidth=2
    )
    ax.axvline(
        x_data.quantile(0.75),
        color="tab:blue",
        linestyle="--",
        alpha=0.3,
        label="Quartiles",
        linewidth=2,
    )

    # Get x limits from config
    lower_lim = plot_sigs_config.loc[plot_sigs_config["column_name"] == sig_name][
        "lower_lim"
    ].values[0]
    upper_lim = plot_sigs_config.loc[plot_sigs_config["column_name"] == sig_name][
        "upper_lim"
    ].values[0]
    ax.set_xlim(x_data.quantile(0.01), x_data.quantile(0.99))
    if sig_name == "avg_IE_SE_signif":
        ax.set_xlim(0, 0.5)

    unit_label = plot_sigs_config.loc[plot_sigs_config["column_name"] == sig_name][
        "unit"
    ].values[0]
    # ax.set_xlabel(
    # f"{sig_name} {unit_label}", fontsize=fontsize, labelpad=10
    # )  # Increased labelpad from default
    ax.set_ylabel(None)
    ax.set_yticklabels([])
    ax.set_yticks([])

    # Remove spines except the bottom
    for spine in ax.spines.values():
        if spine.get_linewidth() > 0:
            spine.set_visible(False)
    ax.spines["bottom"].set_visible(True)

    # Add colorbar
    cmap = plt.cm.Blues_r if "_signif" in sig_name else plt.cm.Blues
    norm = plt.Normalize(lower_lim, upper_lim)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)

    # Adjust plot position to make room for colorbar
    ax.set_position([0.15, 0.25, 0.8, 0.7])  # [left, bottom, width, height]

    # Place colorbar below plot
    cbar_ax = fig.add_axes(
        [0.15, 0.1, 0.8, 0.15]
    )  # [left, bottom, width, height] - increased height from 0.03 to 0.05
    cbar = plt.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    # Set the background of the colorbar to the max color of the colormap
    cbar.ax.set_facecolor(cmap(1.0))
    cbar.set_label(f"{sig_name} {unit_label}", fontsize=fontsize, labelpad=10)

    # Sync colorbar and x-axis ticks
    xticks = ax.get_xticks()
    # increase font size of the cba x ticks
    cbar.ax.tick_params(labelsize=fontsize)
    ax.set_xticks(xticks)
    ax.set_xticklabels([])  # Hide x-axis tick labels
    cbar.set_ticks(xticks)
    ax.tick_params(labelsize=fontsize)

    # Output
    fig_sigs_dir = os.path.join(fig_dir, "fig_sigs")
    if not os.path.exists(fig_sigs_dir):
        os.makedirs(fig_sigs_dir)

    plt.savefig(
        os.path.join(fig_sigs_dir, f"hist_{sig_name}.png"),
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.1,
    )


# %% For all signatures except Wu

sigs_RF_names_ordered = [
    "BFI",
    "BaseflowRecessionK",
    "AverageStorage",
    "RecessionParameters_b",
    "TotalRR",
    "EventRR",
    "Recession_a_Seasonality",
    "VariabilityIndex",
    "avg_IE_SE_thresh",
    "avg_IE_SE_signif",
]

for sigs_name in tqdm(
    sigs_RF_names_ordered,
    desc="Plotting histograms of signature values",
    leave=False,
):
    try:
        warnings.filterwarnings("ignore")
        plot_sig_hist(
            df_sigs,
            sigs_name,
            fig_dir=fig_dir,
        )
    except Exception as e:
        print(f"{sigs_name}: {e}")

# %%
