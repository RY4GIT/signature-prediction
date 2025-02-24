# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

# %%
file_name = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph.csv"
attrs = pd.read_csv(file_name, index_col="gauge_id")
attrs.head()
# %%
var1 = "beta_ave"
var2 = "peakSWEdivP"

# %%
# Drop NaN values for correlation calculation
df = attrs[[var1, var2]].dropna()

# Compute Pearson correlation
pearson_corr, p_value = stats.pearsonr(df[var1], df[var2])

# Plot scatter plot
plt.figure(figsize=(8, 6))
plt.scatter(df[var1], df[var2], alpha=0.5, s=3)
plt.xlabel(var1)
plt.ylabel(var2)
plt.title(
    f"Scatter plot of {var1} vs {var2}\nPearson Correlation: {pearson_corr:.2f} (p={p_value:.3f})"
)
plt.xlim([0, 2])
plt.grid(True)

# Show plot
plt.show()

# %%
