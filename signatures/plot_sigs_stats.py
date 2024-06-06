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
plot_config = pd.read_csv("plot_sig_configs.csv", index_col=0)


# caravan_data = "camels"
# %%
########################################
camels_results_dir = "caravan_camels_20240530" 
hysets_results_dir = "caravan_hysets_20240529"
sig_cat = "McMillan_set"  # 'calc_ALL', or 'McMillan set' 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater'
########################################

# %%
# ______________________________________________________________________________________________
# Load data
def get_sig_results(sig_cat, results_dir):
    if sig_cat == "calc_ALL":
        sigs = pd.read_csv(
            os.path.join(home_dir, sig_output_dir, results_dir, f"out_{sig_cat}.csv")
        )
        sigs.set_index("gauge_id", inplace=True)
    elif sig_cat == "McMillan_set":
        sigs_of = pd.read_csv(
            os.path.join(
                home_dir, sig_output_dir, results_dir, f"out_calc_McMillan_OverlandFlow.csv"
            )
        )
        sigs_of.set_index("gauge_id", inplace=True)
        sigs_gw = pd.read_csv(
            os.path.join(
                home_dir, sig_output_dir, results_dir, f"out_calc_McMillan_Groundwater.csv"
            )
        )
        sigs_gw.set_index("gauge_id", inplace=True)
        sigs = sigs_of.join(sigs_gw, how="outer")

    # Get column names
    _signames = sigs.columns.to_list()
    signames = [s for s in _signames if "_error_str" not in s]
    not_gw_nor_of = [s for s in signames if s not in plot_config["column_name"].tolist()]
    not_calculated = [s for s in plot_config["column_name"].tolist() if s not in signames]

    print("________________________________________________________________________")
    print("Results from:", results_dir)
    print("Size of the results:", len(sigs))
    # print("____________________________________")
    # print("Number of signatures (plot config):", len(plot_config["column_name"].tolist()))
    # print("Number of signatures (results file):",len(signames))
    # print("____________________________________")
    # print("Signature calculated:", signames)
    # print("Calculated but not in the LargeSig paper:", not_gw_nor_of)
    # print("In the LargeSig paper but not calculated:", not_calculated, "\n", "\n")
    

    return sigs
# %%
sigs_camels = get_sig_results(sig_cat, camels_results_dir)
sigs_hysets = get_sig_results(sig_cat, hysets_results_dir)

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
            label="CAMELS-US"
        )
        ax.hist(
            sigs_hysets[row["column_name"]],
            bins=30,
            range=(row["lower_lim"], row["upper_lim"]),
            facecolor="none",
            edgecolor="tab:pink",
            density=True,
            label="HYSETS"
        )
        sns.kdeplot(sigs_camels[row["column_name"]], ax=ax, color='tab:blue')
        sns.kdeplot(sigs_hysets[row["column_name"]], ax=ax, color='tab:pink')
        ax.set_xlabel(f"{row['label']} {row['unit']}")
        ax.set_ylabel("Density")
        # ax.set_xlim([row["lower_lim"], row["upper_lim"]])

    except:
        continue

# Disable unused axes if any
for i in range(num_plots, len(axes)):
    axes[i].axis("off")
    
    # TODO: fix this
    # Check if this is the last plot to add a legend
    if i == num_plots-1:  # Adjust the condition based on your total number of subplots
        axes[i].legend()

# Layout adjustment
plt.tight_layout()
plt.show()

# %%
# ______________________________________________________________________________________________
# Highlight distributions from HUC regions
# %% Get HUCx gauges and results 

# %% Plot them
sigs_camels.head()
# %%

for HUCnum in range(1, 21+1):
    
    prefix = f'camels_{HUCnum:02}'
    print(f"Currently plotting HUC{HUCnum:02}")

    sigs_camels_subset = sigs_camels[[idx.startswith(prefix) for idx in sigs_camels.index]]

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
                label="all gauges in CAMELS-US"
            )
            ax.hist(
                sigs_camels_subset[row["column_name"]],
                bins=30,
                range=(row["lower_lim"], row["upper_lim"]),
                facecolor="none",
                edgecolor="tab:red",
                density=True,
                label=f"gauges in HUC{prefix}"
            )
            sns.kdeplot(sigs_camels[row["column_name"]], ax=ax, color='tab:grey')
            sns.kdeplot(sigs_camels_subset[row["column_name"]], ax=ax, color='tab:red')
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
        if i == num_plots-1:  # Adjust the condition based on your total number of subplots
            axes[i].legend()
            

    # Add a supertitle for the whole figure
    fig.suptitle(f'HUC{HUCnum:02} in red; all camels in grey', fontsize=16)

    # Layout adjustment
    plt.tight_layout()
    plt.show()
    fig.savefig(os.path.join(home_dir, sig_output_dir, camels_results_dir, f"sigdist_HUC{prefix}.png"))
    plt.close()


# %%
# ______________________________________________________________________________________________
# Compare with Sebastian's results for calc_ALLs

sigsall_hysets = get_sig_results("calc_ALL", hysets_results_dir)
sigsall_names = sigsall_hysets.columns.to_list()

Sebastian_results = (
    r"C:\Users\flipl\dev\TOSSH_signatures_Caravan\results\TOSSH_signatures_Caravan.csv"
)
sigs_SG = pd.read_csv(Sebastian_results)
sigs_SG.set_index("gauge_id", inplace=True)
sigs_SG.head()
# %%
compare_SG = sigsall_hysets.join(sigs_SG, lsuffix="_sigs", rsuffix="_sigs_SG", how="left")
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
