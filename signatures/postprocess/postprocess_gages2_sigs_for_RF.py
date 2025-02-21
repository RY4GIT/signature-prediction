# %%
import os
import pandas as pd
import matplotlib.pyplot as plt

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"

gages2_camels_dir = "gages2_camels_20250219"
gages2_hysets_dir = "gages2_hysets_20250219"
out_dir = "gages2_caravan_us_20250219"
origin_caravan_dir = "caravan_us_20250219"

try:
    os.makedirs(os.path.join(sig_dir, out_dir))
except Exception as e:
    print(e)

# %% ################################################################
# CONCAT HYSETS AND CAMELS RESULTS FOR GAGES 2
#####################################################################

out_base_filename = "out_calc_All_custom.csv"
gages2_camels = pd.read_csv(
    os.path.join(sig_dir, gages2_camels_dir, out_base_filename), index_col="gauge_id"
)
gages2_hysets = pd.read_csv(
    os.path.join(sig_dir, gages2_hysets_dir, out_base_filename), index_col="gauge_id"
)
gages2_hysets.dropna(subset=["TotalRR"], inplace=True)

# %%
# Output the concat
gages2_us = pd.concat([gages2_camels, gages2_hysets])
gages2_us.to_csv(os.path.join(sig_dir, out_dir, out_base_filename))
print(
    f"gages2 (CARAVAN {len(gages2_camels)}+ HYSETS {len(gages2_hysets)}) has {len(gages2_us)} gages"
)

# %% ################################################################
# COMPARE THE RESULTS WITH CARAVAN (ERA-5)
#####################################################################

# Get the caravan signatures afterQA
caravan_us_afterQA = pd.read_csv(
    os.path.join(sig_dir, origin_caravan_dir, "out_calc_All_custom_filt_qc.csv"),
    index_col="gauge_id",
)
print(
    f"CARAVAN after removing gages with bad-quality Q, including snowy catchments: {len(caravan_us_afterQA)}"
)

caravan_us_afterQA_excluSnow = pd.read_csv(
    filepath_or_buffer=os.path.join(
        sig_dir, origin_caravan_dir, "out_calc_All_custom_filt_qc_snow.csv"
    ),
    index_col="gauge_id",
)
print(
    f"Excluding snowy catchments for Event signatures: {caravan_us_afterQA_excluSnow['IE_thresh'].notna().sum()}"
)

# %%
fig_dir = "figs"
try:
    os.makedirs(os.path.join(sig_dir, out_dir, fig_dir))
except Exception as e:
    print(e)

# %%
merged_df = gages2_us.merge(
    caravan_us_afterQA, on="gauge_id", suffixes=("_gages2", "_caravan"), how="inner"
)
print(f"Caravan after QA: {len(caravan_us_afterQA)}")
print(f"GAGES2: {len(gages2_us)}")
print(f"Joined left on GAGES2: {len(merged_df)}")
print("<- this should be equal or smaller than Caravan or GAGES2 gage numbers")

# %%
plot_config_path = (
    r"C:\Users\flipl\dev\signature-prediction\signatures\visualize\plot_sigs_config.csv"
)
plot_configs = pd.read_csv(plot_config_path)
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
    # ax.set_xlim(plot_config["lower_lim"], plot_config["upper_lim"])
    # ax.set_ylim(plot_config["lower_lim"], plot_config["upper_lim"])

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
common_gages = merged_df.index

filtered_caravan_us_afterQA = caravan_us_afterQA.loc[common_gages]
filtered_gages2_us_afterQA = gages2_us.loc[common_gages]

# %%

filtered_caravan_us_afterQA.to_csv(
    os.path.join(
        sig_dir, origin_caravan_dir, "out_calc_All_custom_filt_qc_gages2subset.csv"
    )
)
# %%
filtered_gages2_us_afterQA.to_csv(
    os.path.join(sig_dir, out_dir, "out_calc_All_custom_filt_qc_caravanoverlap.csv")
)

# %% ################################################################
# Repeat the same for the low-snow catchments
#####################################################################


merged_df_lowsnow = gages2_us.merge(
    caravan_us_afterQA_excluSnow,
    on="gauge_id",
    suffixes=("_gages2", "_caravan"),
    how="inner",
)


# %%
common_gages_lowsnow = merged_df_lowsnow.index
filtered_caravan_us_lowsnow = caravan_us_afterQA_excluSnow.loc[common_gages_lowsnow]
filtered_gages2_us_lowsnow = gages2_us.loc[common_gages_lowsnow]

filtered_caravan_us_lowsnow.to_csv(
    path_or_buf=os.path.join(
        sig_dir, origin_caravan_dir, "out_calc_All_custom_filt_qc_snow_gages2subset.csv"
    )
)

filtered_gages2_us_lowsnow.to_csv(
    path_or_buf=os.path.join(
        sig_dir, out_dir, "out_calc_All_custom_filt_qc_snow_caravanoverlap.csv"
    )
)

print(f"Caravan after QA and snow: {len(caravan_us_afterQA_excluSnow)}")
print(f"GAGES2: {len(gages2_us)}")
print(f"Joined left on GAGES2: {len(merged_df_lowsnow)}")
print(f"<- this should be equal or smaller than Caravan or GAGES2 gage numbers")
print(
    f"<- the value should equal to {len(filtered_caravan_us_lowsnow)} and {len(filtered_gages2_us_lowsnow)}"
)
print(
    f"Event signatures are only available at: {filtered_gages2_us_lowsnow['IE_thresh'].notna().sum()}"
)

# %%
