# %%
import os
import pandas as pd
import numpy as np

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"

gridmet_sigs_dir = "gages2_20250608"
caravan_sigs_dir = "caravan_us_20250525"

gridmet_sigs_file = os.path.join(sig_dir, gridmet_sigs_dir, "out_calc_All_custom.csv")
caravan_sigs_file = os.path.join(
    sig_dir, caravan_sigs_dir, "out_calc_All_custom_filt_qc_snow_area.csv"
)

# %%
gridmet_sigs = pd.read_csv(gridmet_sigs_file)
gridmet_sigs["gauge_id"] = gridmet_sigs["gauge_id"].astype(str)
caravan_sigs = pd.read_csv(caravan_sigs_file)
caravan_sigs["gauge_num"] = caravan_sigs["gauge_num"].astype(str).str.zfill(8)

# %%
df = pd.merge(
    gridmet_sigs,
    caravan_sigs,
    left_on="gauge_id",
    right_on="gauge_num",
    how="left",
    suffixes=("_gridmet", "_caravan"),
)
df.head()
# %%
plot_config_file = (
    r"C:\Users\flipl\dev\signature-prediction\signatures\visualize\plot_sigs_config.csv"
)
plot_config = pd.read_csv(plot_config_file)
plot_config.head()
# %%
import matplotlib.pyplot as plt
import scipy.stats

ncols = 4
nrows = len(plot_config) // ncols
fig, axs = plt.subplots(nrows, ncols, figsize=(12, 20))
axs = axs.flatten()
for i, row in plot_config.iterrows():
    sig_name = row["column_name"]
    try:
        gages2_sig = df[sig_name + "_gridmet"]
        caravan_sig = df[sig_name + "_caravan"]

        # Clean the data
        gages2_sig_clean = gages2_sig.replace([np.inf, -np.inf], np.nan)
        caravan_sig_clean = caravan_sig.replace([np.inf, -np.inf], np.nan)

        # Create mask for valid data
        mask = gages2_sig_clean.notna() & caravan_sig_clean.notna()

        # Get clean data
        gages2_clean = gages2_sig_clean[mask]
        caravan_clean = caravan_sig_clean[mask]

        if len(gages2_clean) > 0 and len(caravan_clean) > 0:
            # Calculate correlation
            corr, _ = scipy.stats.pearsonr(gages2_clean, caravan_clean)

            # Get plot limits
            sig_min = row["lower_lim"]
            sig_max = row["upper_lim"]

            # Plot
            axs[i].plot([sig_min, sig_max], [sig_min, sig_max], "k--", alpha=0.5)
            axs[i].scatter(
                gages2_clean,
                caravan_clean,
                alpha=0.5,
                label=f"Pearson corr: {corr:.2f}",
                s=1,
            )

            axs[i].set_title(sig_name)
            axs[i].set_xlabel("gages2")
            axs[i].set_ylabel("caravan")
            axs[i].set_xlim(sig_min, sig_max)
            axs[i].set_ylim(sig_min, sig_max)
            axs[i].legend()

    except Exception as e:
        print(f"Error processing {sig_name}: {str(e)}")

plt.tight_layout()
plt.show()


# %%
