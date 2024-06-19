# %%
# Plot the distribution of signatures calculated from caravan (calculate_sigs_caravan.m)
# Ryoko Araki (@ry4git), 2024

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns


home_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
data_dir = "data"
sig_output_dir = r"out\signatures"
fig_dir = "figs"
output_dir = "out"
plot_config = pd.read_csv("plot_sigs_config.csv", index_col=0)
hysets_qa = pd.read_csv(
    os.path.join(
        home_dir, output_dir, "caravan_datacheck", "hysets_summary_w_manualflag.csv"
    ),
    index_col="gauge_id",
)
hysets_attrs = pd.read_csv(
    os.path.join(
        home_dir,
        data_dir,
        "Caravan1.4",
        "attributes",
        "hysets",
        "attributes_other_hysets.csv",
    ),
    index_col="gauge_id",
)
hysets_qa = hysets_qa.join(hysets_attrs)
# caravan_data = "camels"
# %%
########################################
# Directory
camels_results_dir = "caravan_camels_20240609"
hysets_results_dir = "caravan_hysets_20240609"
sig_cat = "calc_All_custom"  # 'calc_All_custom', 'calc_All', or 'McMillan set' 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater'

########################################
# Hysets quality control threshold
subset_nan_fraction_thresh = 0.3
duration_thresh = 5
Q95_thresh = 1.0
########################################

# %%
# Calculate some stats
hysets_qa["start_date"] = pd.to_datetime(hysets_qa["start_date"])
hysets_qa["end_date"] = pd.to_datetime(hysets_qa["end_date"])
hysets_qa["start_year"] = hysets_qa["start_date"].dt.year
hysets_qa["end_year"] = hysets_qa["end_date"].dt.year
hysets_qa["duration_yr"] = (
    hysets_qa["end_date"] - hysets_qa["start_date"]
).dt.days / 365
hysets_qa["qf_subset_nan_fraction"] = (
    hysets_qa["subset_nan_fraction"] < subset_nan_fraction_thresh
)
hysets_qa["qf_duration"] = hysets_qa["duration_yr"] > duration_thresh
# hysets_qa["qf_manualcheck"] = ~hysets_qa["manual_check"].notna()
# hysets_qa["qf_Q95"] = hysets_qa["Q95"] > Q95_thresh
hysets_qa["qf_overall"] = hysets_qa["qf_subset_nan_fraction"] & hysets_qa["qf_duration"]


# %%
# ______________________________________________________________________________________________
# Load data
def get_sig_results(sig_cat, results_dir):
    if (sig_cat == "calc_All") | (sig_cat == "calc_All_custom"):
        sigs = pd.read_csv(
            os.path.join(home_dir, sig_output_dir, results_dir, f"out_{sig_cat}.csv")
        )
        sigs.set_index("gauge_id", inplace=True)
    elif sig_cat == "McMillan_set":
        sigs_of = pd.read_csv(
            os.path.join(
                home_dir,
                sig_output_dir,
                results_dir,
                f"out_calc_McMillan_OverlandFlow.csv",
            )
        )
        sigs_of.set_index("gauge_id", inplace=True)
        sigs_gw = pd.read_csv(
            os.path.join(
                home_dir,
                sig_output_dir,
                results_dir,
                f"out_calc_McMillan_Groundwater.csv",
            )
        )
        sigs_gw.set_index("gauge_id", inplace=True)
        sigs = sigs_of.join(sigs_gw, how="outer")

    print("________________________________________________________________________")
    print("Results from:", results_dir)
    print("Size of the results:", len(sigs))

    return sigs


# %%
_sigs_camels = get_sig_results(sig_cat, camels_results_dir)
sigs_camels = _sigs_camels
# sigs_camels = _sigs_camels[_sigs_camels["Q95"]>Q95_thresh]
print(f"Passed quality control: {len(sigs_camels)}")
_sigs_hysets = get_sig_results(sig_cat, hysets_results_dir)
_sigs_hysets = _sigs_hysets.join(hysets_qa.drop(columns=["Q95"]))
sigs_hysets = _sigs_hysets[_sigs_hysets["qf_overall"] == True]
print(f"Passed quality control: {len(sigs_hysets)}")
# %%
# ______________________________________________________________________________________________
# Plot histogram of signatures for overland flow & groundwater signatures

# Number of rows for 4 plots per row
num_plots = len(plot_config)
num_rows = (num_plots + 3) // 4  # Ceiling division to ensure all plots fit
fig, axes = plt.subplots(
    nrows=num_rows, ncols=4, figsize=(15, 2.5 * num_rows)
)  # Adjust the size as needed
axes = axes.flatten()  # Flatten the axes array for easy iteration


# Plot each histogram
for ax, (index, row) in zip(axes, plot_config.iterrows()):
    try:
        ax.hist(
            sigs_camels[row["column_name"]],
            bins=30,
            range=(row["lower_lim"], row["upper_lim"]),
            facecolor="none",
            edgecolor="tab:blue",
            density=True,
            label="CAMELS-US",
        )
        ax.hist(
            sigs_hysets[row["column_name"]],
            bins=30,
            range=(row["lower_lim"], row["upper_lim"]),
            facecolor="none",
            edgecolor="tab:pink",
            density=True,
            label="HYSETS",
        )
        sns.kdeplot(
            sigs_camels[row["column_name"]],
            ax=ax,
            color="tab:blue",
            clip=[row["lower_lim"], 9999],
        )
        sns.kdeplot(
            sigs_hysets[row["column_name"]],
            ax=ax,
            color="tab:pink",
            clip=[row["lower_lim"], 9999],
        )  # , clip=[row["lower_lim"], row["upper_lim"]])
        ax.set_xlabel(f"{row['label']} {row['unit']}")
        ax.set_ylabel("Density")
        # ax.set_xlim([row["lower_lim"], row["upper_lim"]])
        plt.tight_layout()
    except:
        continue

# Disable unused axes if any
for i in range(num_plots, len(axes)):
    axes[i].axis("off")

    # TODO: fix this
    # Check if this is the last plot to add a legend
    if (
        i == num_plots - 1
    ):  # Adjust the condition based on your total number of subplots
        axes[i].legend()

# Layout adjustment
plt.tight_layout()
plt.show()

# %% ##############################################################################
# Check extremely large values of signatures
##############################################################################

sig_key = "Storage_thresh"
sig_value_thresh = 5000
sig_extreme = sigs_hysets[sigs_hysets[sig_key] > sig_value_thresh][[sig_key]]
print(sig_extreme)
print(sig_extreme.index)

# %%
# Get data and plot
target_gauge_id = "hysets_14242511"  # sig_extreme.index.item()
data = pd.read_csv(
    os.path.join(
        home_dir,
        data_dir,
        "Caravan1.4",
        "timeseries",
        "csv",
        "hysets",
        f"{target_gauge_id}.csv",
    ),
    parse_dates=["date"],
    index_col="date",
)
start_date = data[data["streamflow"].notna()].index[0]
end_date = data[data["streamflow"].notna()].index[-1]
ax = data.streamflow[start_date:end_date].plot()
ax.set_ylabel("streamflow (mm/d)")
ax.set_title(
    f"{target_gauge_id}: {hysets_qa.loc[target_gauge_id].gauge_name}",  # \n{sig_key}={sigs_hysets.loc[target_gauge_id][sig_key]:.3f}",
    fontsize=15,
)
# ax.set_ylim([0, 0.1])
fig = ax.get_figure()  # Get the figure object associated with the axis
fig.autofmt_xdate()  # Apply auto-formatting of the dates on the x-axis

# print next gauges to check
print(sig_extreme.index)


# %%%

# %%
# print(f"Q50: {data.streamflow.quantile(0.5)}")
# print(f"Q95: {data.streamflow.quantile(0.95)}")
# # %%
# hysets_qa.loc[sig_extreme_gauge_id]

# # Sort data
# x = np.sort(data.streamflow.dropna())
# # Calculate CDF values
# y = np.arange(1, len(x) + 1)

# plt.figure(figsize=(8, 4))  # Optional: adjusts the size of the plot
# plt.plot(x, y, marker=".", linestyle="none")  # 'none' for no line
# plt.title("CDF of Streamflow")
# plt.xlabel("Streamflow")
# plt.ylabel("CDF")
# plt.grid(True)  # Optional: adds a grid
# plt.show()


# %%

# %%
# ______________________________________________________________________________________________
# Highlight distributions from HUC regions
# %% Get HUCx gauges and results

# %% Plot them
sigs_camels.head()
# %%

for HUCnum in range(1, 21 + 1):

    prefix = f"camels_{HUCnum:02}"
    print(f"Currently plotting HUC{HUCnum:02}")

    sigs_camels_subset = sigs_camels[
        [idx.startswith(prefix) for idx in sigs_camels.index]
    ]

    # Number of rows for 4 plots per row
    num_plots = len(plot_config)
    num_rows = (num_plots + 3) // 4  # Ceiling division to ensure all plots fit
    fig, axes = plt.subplots(
        nrows=num_rows, ncols=4, figsize=(15, 2.5 * num_rows)
    )  # Adjust the size as needed
    axes = axes.flatten()  # Flatten the axes array for easy iteration

    # Plot each histogram
    for ax, (index, row) in zip(axes, plot_config.iterrows()):
        try:
            ax.hist(
                sigs_camels[row["column_name"]],
                bins=30,
                range=(row["lower_lim"], row["upper_lim"]),
                facecolor="none",
                edgecolor="tab:grey",
                density=True,
                label="all gauges in CAMELS-US",
            )
            ax.hist(
                sigs_camels_subset[row["column_name"]],
                bins=30,
                range=(row["lower_lim"], row["upper_lim"]),
                facecolor="none",
                edgecolor="tab:red",
                density=True,
                label=f"gauges in HUC{prefix}",
            )
            sns.kdeplot(sigs_camels[row["column_name"]], ax=ax, color="tab:grey", cut=0)
            sns.kdeplot(
                sigs_camels_subset[row["column_name"]], ax=ax, color="tab:red", cut=0
            )
            ax.set_xlabel(f"{row['label']} {row['unit']}")
            ax.set_ylabel("Density")
            ax.set_xlim([row["lower_lim"], row["upper_lim"]])

        except:
            continue

    # Disable unused axes if any
    for i in range(num_plots, len(axes)):
        axes[i].axis("off")

        # TODO: fix this
        # Check if this is the last plot to add a legend
        if (
            i == num_plots - 1
        ):  # Adjust the condition based on your total number of subplots
            axes[i].legend()

    # Add a supertitle for the whole figure
    fig.suptitle(f"HUC{HUCnum:02} in red; all camels in grey", fontsize=16)

    # Layout adjustment
    plt.tight_layout()
    plt.show()
    fig.savefig(
        os.path.join(
            home_dir, sig_output_dir, camels_results_dir, f"sigdist_HUC{prefix}.png"
        )
    )
    plt.close()


# %%
# ______________________________________________________________________________________________
# Compare with Sebastian's results for calc_ALLs

sigsall_hysets = get_sig_results("calc_All", hysets_results_dir)
sigsall_names = sigsall_hysets.columns.to_list()

Sebastian_results = (
    r"C:\Users\flipl\dev\TOSSH_signatures_Caravan\results\TOSSH_signatures_Caravan.csv"
)
sigs_SG = pd.read_csv(Sebastian_results)
sigs_SG.set_index("gauge_id", inplace=True)
sigs_SG.head()
# %%
compare_SG = sigsall_hysets.join(
    sigs_SG, lsuffix="_sigs", rsuffix="_sigs_SG", how="left"
)
# compare_SG.head()

# Determine the number of rows needed based on the number of signals
num_signals = len(sigsall_names)
num_cols = 4
num_rows = (
    num_signals + num_cols - 1
) // num_cols  # Compute the required number of rows

# Create the subplots
fig, axes = plt.subplots(
    nrows=num_rows, ncols=num_cols, figsize=(15, 2.5 * num_rows)
)  # Adjust the size as needed
axes = axes.flatten()  # Flatten the axes array to make it easier to iterate

# Plotting
for i, col in enumerate(sigsall_names):
    try:
        ax = axes[i]

        data_x = compare_SG[col + "_sigs_SG"]
        data_y = compare_SG[col + "_sigs"]

        # Exclude NaNs for quantile calculation
        valid_data_x = data_x.dropna()

        min_val = np.quantile(valid_data_x, 0.0001)
        max_val = np.quantile(valid_data_x, 0.9999)

        ax.scatter(data_x, data_y, alpha=0.5)
        ax.plot([min_val, max_val], [min_val, max_val], "--", color="grey")

        ax.set_xlabel(f"Sebastian")
        ax.set_ylabel(f"Ryoko")
        ax.set_title(f"{col}")
    except:
        continue

# # Disable unused axes if there are any
# for i in range(num_signals, len(axes)):
#     axes[i].axis("off")

plt.tight_layout()
plt.show()
# %%
# Compare Anni'es signature and mine
# ______________________________________________________________________________________________
# Compare with Sebastian's results for calc_ALLs

sigsall_hysets = get_sig_results("calc_All", hysets_results_dir)
sigsall_names = sigsall_hysets.columns.to_list()

Sebastian_results = (
    r"C:\Users\flipl\dev\TOSSH_signatures_Caravan\results\TOSSH_signatures_Caravan.csv"
)
sigs_SG = pd.read_csv(Sebastian_results)
sigs_SG.set_index("gauge_id", inplace=True)
sigs_SG.head()
# %%


sigs_camels_raraki = get_sig_results(
    "calc_All", "caravan_camels_20240530_defaultparams"
)  # pd.read_csv(
# r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20240530_defaultparams\out_calc_All.csv",
# index_col="gauge_id",
# )
sigs_camels_aholt = pd.read_csv(
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\Signatures\sigs_camels_v2.csv",
    index_col="gauge_id",
)
sigsall_names = sigs_camels_raraki.columns.to_list()  # ["TotalRR", "EventRR"]  #
# sigs_camels_aholt.rename(columns={""})
# sigs_camels_aholt.columns
print(sigsall_names)
# %%
# Determine the number of rows needed based on the number of signals
num_signals = len(sigsall_names)
num_cols = 4
num_rows = (
    num_signals + num_cols - 1
) // num_cols  # Compute the required number of rows

# Create the subplots
fig, axes = plt.subplots(
    nrows=num_rows, ncols=num_cols, figsize=(15, 2.5 * num_rows)
)  # Adjust the size as needed
axes = axes.flatten()  # Flatten the axes array to make it easier to iterate

# Plotting
for i, col in enumerate(sigsall_names):
    try:
        ax = axes[i]

        data_x = sigs_camels_aholt[col]
        data_y = sigs_camels_raraki[col]

        # Exclude NaNs for quantile calculation
        valid_data_x = data_x.dropna()

        min_val = np.quantile(valid_data_x, 0.0001)
        max_val = np.quantile(valid_data_x, 0.9999)

        ax.scatter(data_x, data_y, alpha=0.5)
        ax.plot([min_val, max_val], [min_val, max_val], "--", color="grey")

        ax.set_xlabel(f"Annie")
        ax.set_ylabel(f"Ryoko")
        ax.set_title(f"{col}")
    except:
        continue

plt.tight_layout()
# %%
