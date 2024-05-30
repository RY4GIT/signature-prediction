# %%
# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

home_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
data_dir = "data"
sig_output_dir = r"out\signatures"
caravan_data = "hysets"
fig_dir = "figs"

# %%
########################################
results_dir = "caravan_hysets_20240529"
sig_cat = "calc_McMillan_OverlandFlow"  # 'calc_ALL', 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater'
########################################

# %%
# ______________________________________________________________________________________________
# Load data
sigs = pd.read_csv(
    os.path.join(home_dir, sig_output_dir, results_dir, f"out_{sig_cat}.csv")
)
sigs.set_index("gauge_id", inplace=True)
plot_config = pd.read_csv("plot_sig_configs.csv", index_col=0)

# Get column names
_signames = sigs.columns.to_list()
signames = [s for s in _signames if "_error_str" not in s]
not_gw_nor_of = [s for s in signames if s not in plot_config["name"].tolist()]
not_calculated = [s for s in plot_config["name"].tolist() if s not in signames]
print("Calculated but not in the LargeSig paper:", not_gw_nor_of)
print("Not calculated:", not_calculated)
print(len(plot_config["name"].tolist()))
print(len(signames))
print(len(not_gw_nor_of))

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

import seaborn as sns

# Plot each histogram
for ax, (index, row) in zip(axes, plot_config.iterrows()):
    try:
        data = sigs[row["name"]]
        ax.hist(
            data,
            bins=30,
            range=(row["lower_lim"], row["upper_lim"]),
            facecolor="none",
            edgecolor="tab:blue",
            density=True,
        )
        # sns.kdeplot(data, ax=ax, color='tab:blue')
        ax.set_xlabel(f"{row['name']} {row['unit']}")
        ax.set_ylabel("Density")
        ax.set_xlim([row["lower_lim"], row["upper_lim"]])
    except:
        continue

# Disable unused axes if any
for i in range(num_plots, len(axes)):
    axes[i].axis("off")

# Layout adjustment
plt.tight_layout()
plt.show()

# %%
# ______________________________________________________________________________________________
# Compare with Sebastian's results
Sebastian_results = (
    r"C:\Users\flipl\dev\TOSSH_signatures_Caravan\results\TOSSH_signatures_Caravan.csv"
)
sigs_SG = pd.read_csv(Sebastian_results)
sigs_SG.set_index("gauge_id", inplace=True)
# sigs_SG.head()

compare_SG = sigs.join(sigs_SG, lsuffix="_sigs", rsuffix="_sigs_SG", how="left")
# compare_SG.head()

# Determine the number of rows needed based on the number of signals
num_signals = len(signames)
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
for i, col in enumerate(signames):
    try:
        ax = axes[i]
        ax.scatter(compare_SG[col + "_sigs_SG"], compare_SG[col + "_sigs"], alpha=0.5)
        # Adding a y=x reference line
        min_val = min(
            compare_SG[col + "_sigs_SG"].min(), compare_SG[col + "_sigs"].min()
        )
        max_val = max(
            compare_SG[col + "_sigs_SG"].max(), compare_SG[col + "_sigs"].max()
        )
        ax.plot([min_val, max_val], [min_val, max_val], "--", color="tab:grey")

        ax.set_xlabel(f"Sebastian")
        ax.set_ylabel(f"Ryoko")
        ax.set_title(f"{col}")
    except:
        continue

# Disable unused axes if there are any
for i in range(num_signals, len(axes)):
    axes[i].axis("off")

plt.tight_layout()
plt.show()
# %%
