# %%
import os
import pandas as pd
import matplotlib.pyplot as plt

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"

gages2_camels_dir = "gages2_camels_20250210"
gages2_hysets_dir = "gages2_hysets_20250211"
out_filename = "out_calc_All_custom.csv"
out_dir = "gages2_caravan_us_20250211"

try:
    os.makedirs(os.path.join(sig_dir, out_dir))
except Exception as e:
    print(e)

# %% ################################################################
# CONCAT HYSETS AND CAMELS RESULTS FOR GAGES 2
#####################################################################
gages2_camels = pd.read_csv(
    os.path.join(sig_dir, gages2_camels_dir, out_filename), index_col="gauge_id"
)
gages2_hysets = pd.read_csv(
    os.path.join(sig_dir, gages2_hysets_dir, out_filename), index_col="gauge_id"
)
gages2_hysets.dropna(subset=["TotalRR"], inplace=True)
# %%

gages2_us = pd.concat([gages2_camels, gages2_hysets])
gages2_us.to_csv(os.path.join(sig_dir, out_dir, out_filename))

# %% ################################################################
# COMPARE THE RESULTS WITH CARAVAN (ERA-5)
#####################################################################

origin_caravan_dir = "caravan_us_20240609_tunedparams"
caravan_us = pd.read_csv(
    os.path.join(sig_dir, origin_caravan_dir, out_filename), index_col="gauge_id"
)

# %%
fig_dir = "figs"
try:
    os.makedirs(os.path.join(sig_dir, out_dir, fig_dir))
except Exception as e:
    print(e)

# %%
merged_df = gages2_us.merge(caravan_us, on="gauge_id", suffixes=("_gages2", "_caravan"))
merged_df

# %%
plot_configs = pd.read_csv("plot_sigs_config.csv")
plot_configs

# %%


def plot_scatter_comparison(df, plot_config, save_path=None):
    """
    Plots scatter comparisons for each signal in plot_configs, overlaying a 1:1 reference line.

    Parameters:
    - gages2_us (pd.DataFrame): DataFrame containing GAGES II data.
    - caravan_us (pd.DataFrame): DataFrame containing Caravan data.
    - plot_configs (pd.DataFrame): DataFrame with configuration details for plotting.
    - save_path (str): Directory to save the figures.
    """
    col_name = plot_config["column_name"]
    x_var = f"{col_name}_gages2"
    y_var = f"{col_name}_caravan"

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Determine min and max values for 1:1 line
    min_val = min(df[x_var].min(), df[y_var].min())
    max_val = max(df[x_var].max(), df[y_var].max())

    # Plot 1:1 reference line
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        "--",
        color="lightgrey",
        label="1:1 Line",
    )

    # Scatter plot
    ax.scatter(
        df[x_var],
        df[y_var],
        alpha=0.7,
        edgecolors="k",
    )

    # if col_name.endswith("_thresh"):
    ax.set_xlim(plot_config["lower_lim"], plot_config["upper_lim"])
    ax.set_ylim(plot_config["lower_lim"], plot_config["upper_lim"])

    # Labels and title
    ax.set_xlabel("GAGES II (gridMET)")
    ax.set_ylabel("Caravan (ERA-5)")
    ax.set_title(plot_config["label"])
    ax.legend()
    ax.grid(True)

    # Save figure
    save_file = os.path.join(save_path, f"sig_comparison_{col_name}.png")
    fig.savefig(save_file, dpi=300, bbox_inches="tight")
    plt.close(fig)  # Close figure to free memory

    print(f"Saved: {save_file}")


# Loop through each row in plot_configs
save_path = os.path.join(sig_dir, out_dir, fig_dir)
for _, plot_config in plot_configs.iterrows():
    plot_scatter_comparison(merged_df, plot_config, save_path=save_path)

# %%
