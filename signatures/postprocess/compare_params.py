# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# %%
df_adj = pd.read_csv(
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20260714\out_calc_All_custom_shortlist.csv"
)
df = pd.read_csv(
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20250525\out_calc_All_custom.csv"
)

# %%
df_adj.set_index("gauge_id", inplace=True)
df.set_index("gauge_id", inplace=True)

# %%
df = df.join(df_adj.add_suffix("_adj"), how="left")

# %%
df.set_index("gauge_id", inplace=True)

# %%
df
# %%
sig_names = [
    "BFI",
    "BaseflowRecessionK",
    "AverageStorage",
    "RecessionParameters_b",
    "TotalRR",
    "EventRR",
    "Recession_a_Seasonality",
    "VariabilityIndex",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "IE_thresh",
    "SE_thresh",
    # "avg_IE_SE_thresh",
    # "avg_IE_SE_signif",
]
# %%
from scipy.stats import pearsonr, spearmanr

fig, axes = plt.subplots(4, 4, figsize=(12, 12))
axes = axes.flatten()
for i, sig_name in enumerate(sig_names):
    ax = axes[i]
    x = df[sig_name]
    y = df[sig_name + "_adj"]

    # Drop NaNs for correlation calculation
    valid = x.notna() & y.notna()
    x_valid = x[valid]
    y_valid = y[valid]

    # Pearson and Spearman correlation
    if len(x_valid) > 1:
        pearson_corr, pearson_p = pearsonr(x_valid, y_valid)
        spearman_corr, spearman_p = spearmanr(x_valid, y_valid)
    else:
        pearson_corr, spearman_corr = np.nan, np.nan

    ax.scatter(x, y, alpha=0.7, s=5)
    # add 1:1 line
    min_val = np.nanmin([x.min(), y.min()])
    max_val = np.nanmax([x.max(), y.max()])
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        "--",
        linewidth=1,
        color="lightgray",
        alpha=0.5,
    )
    ax.set_xlabel(sig_name)
    ax.set_ylabel(sig_name + "_adj")
    ax.set_title(sig_name)

    # Add correlation to legend (rounded for readability)
    corr_label = (
        f"Pearson r={pearson_corr:.2f}\nSpearman ρ={spearman_corr:.2f}"
        if np.isfinite(pearson_corr) and np.isfinite(spearman_corr)
        else "correlation: n/a"
    )
    ax.legend(title=corr_label, loc="best")
plt.suptitle("CAMELS")

# Hide empty subplot if sig_names < 16
for j in range(len(sig_names), 16):
    fig.delaxes(axes[j])
plt.tight_layout()
plt.show()
# %%
