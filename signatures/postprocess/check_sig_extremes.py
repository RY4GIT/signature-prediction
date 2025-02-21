# %%
# Investigate why IE_thresh and SE_slope has very low predictability.

import os
import pandas as pd
import matplotlib.pyplot as plt
# %%

sigs_obs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20250219\out_calc_All_custom_filt_qc_snow.csv"
sigs_obs = pd.read_csv(sigs_obs_file, index_col="gauge_id")
sigs_pred_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf\archive\output_raraki_20250211_gages2exp_baseline_withoutsnow\predicted_signatures.csv"
sigs_pred = pd.read_csv(sigs_pred_file, index_col="gauge_id")
# %%
sigs_obs.head()
# %%
sigs_pred.head()
# %%
sig_name = "VariabilityIndex"

target_sig_obs = sigs_obs[sig_name].copy()
target_sig_obs.rename("observed", inplace=True)
# %%
target_sig_pred = sigs_pred[sigs_pred["sig_name"] == sig_name]
target_sig_pred
# %%
target_sig = target_sig_pred.join(target_sig_obs)
# %%
# Create scatter plot
plt.figure(figsize=(6, 6))
plt.scatter(target_sig["prediction"], target_sig["observed"], alpha=0.7, edgecolors="k")

# Labels and title
plt.xlabel("Prediction")
plt.ylabel("Observed")
plt.title(sig_name)
# plt.ylim([0, 100])
# Display the plot
plt.grid(True)
plt.show()

# %% Print out ridiculously high IEthresh
target_sig[target_sig["observed"] > 2].to_clipboard()
# %%
