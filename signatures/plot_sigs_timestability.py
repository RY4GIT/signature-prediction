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
caravan_dir = r"Caravan1.4"
attributes_dir = "attributes"
caravan_data = "camels"
data_type="csv"
fig_dir = "figs"
plot_config = pd.read_csv("plot_sig_configs.csv", index_col=0)

attrs_geo = pd.read_csv(os.path.join(home_dir, data_dir, caravan_dir, attributes_dir, caravan_data, f"attributes_other_{caravan_data}.{data_type}"))
attrs_geo.set_index("gauge_id")
attrs_geo_names = attrs_geo.columns.to_list()
attrs_geo.head()

gauge_ids = attrs_geo["gauge_id"][attrs_geo["gauge_id"].str.startswith(f'{caravan_data}_')].tolist()

# caravan_data = "camels"
# %%
########################################
camels_results_dir = "caravan_camels_timestability_20240606" 
sig_cat = "calc_ALL"  # 'calc_ALL', or 'McMillan set' 'calc_McMillan_OverlandFlow', 'calc_McMillan_Groundwater'
########################################

# %%
num_plots = len(plot_config)
num_rows = (num_plots + 3) // 4  # Ceiling division to ensure all plots fit
# Number of rows for 4 plots per row
plt.rcParams['font.size'] = 12
fig, axes = plt.subplots(
    nrows=num_rows, ncols=4, figsize=(15, 2.5 * num_rows)
)  # Adjust the size as needed
axes = axes.flatten()  # Flatten the axes array for easy iteration

# ______________________________________________________________________________________________
# Load data
for i, gauge_id in enumerate(gauge_ids[:4]):
    # ______________________________________________________________________________________________
    # Get the data

    # gauge_id = "camels_01013500"
    sigs = pd.read_csv(
        os.path.join(home_dir, sig_output_dir, camels_results_dir, f"out_{sig_cat}_{gauge_id}.csv")
    )
    sigs.set_index("gauge_id", inplace=True)
    sigs["duration"] = sigs["end_year"] - sigs["start_year"]

    # ______________________________________________________________________________________________
    # Plot histogram of signatures for overland flow & groundwater signatures

    # Plot each histogram
    for ax, (index, row) in zip(axes, plot_config.iterrows()):
        try:
            ax.plot(sigs["duration"], sigs[row['column_name']],alpha=0.3, color="tab:blue")

            if i==0:
                ax.set_ylabel(f"{row['label']} {row['unit']}")
                # Set x-ticks every 5 units, turn off labels for intermediate ticks
                x_ticks = np.arange(0, max(sigs["duration"]) + 5, 5)
                ax.set_xlabel("Duration (year)")
                ax.set_xticks(x_ticks)  # Set major ticks every 5
                # ax.set_xticklabels([str(tick) if (tick % 2.5 == 0) else "" for tick in x_ticks])
        except:
            continue

    if i==0:
        # Disable unused axes if any
        for j in range(num_plots, len(axes)):
            axes[j].axis("off")
            
            # TODO: fix this
            # Check if this is the last plot to add a legend
            if j == num_plots-1:  # Adjust the condition based on your total number of subplots
                axes[j].legend()

    del sigs

# Layout adjustment
plt.tight_layout()
plt.show()
# %%
