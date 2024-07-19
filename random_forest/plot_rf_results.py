# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# %%
# ____________________________________________________________________________________
# Config
results_dir = r"G:/Shared drives/Signatures -- large scale/baseflow/RAraki/out/rf/"
output_dir = r"output_20240619_reproduce_aholt_usingCaravanDerivedSigs"


# ____________________________________________________________________________________
# Load data
df_imp = pd.read_csv(os.path.join(results_dir, output_dir, "var_importance.csv"))
print(df_imp.head())
df_r2 = pd.read_csv(
    os.path.join(results_dir, output_dir, "r_squared.csv"), index_col="sig_name"
)
print(df_r2.head(10))

# %%
# ____________________________________________________________________________________
# Plotting functions

#########################################################
# Plot %incMSE by predictor
#########################################################

# Customize color by predictor
color_mapping = {
    "geol_weighted_ave_age_ma": "red",
    "isowet_areafrac": "blue",
    "p_seasonality": "dimgrey",
    "frac_snow": "dimgrey",
    "low_prec_dur": "dimgrey",
    "low_prec_freq": "dimgrey",
    "aridity": "dimgrey",
}


# Function to map colors
def map_colors(predictor):
    return color_mapping.get(predictor, "lightgrey")


# Apply the mapping function to the dataframe
df_imp["color"] = df_imp["predictor"].apply(map_colors)
# Create a dictionary mapping each predictor to its color
color_dict = df_imp.set_index("predictor")["color"].to_dict()
# ______________________________________________________________
# Assuming df_imp is your dataframe
sigs = [
    "EventRR",
    "TotalRR",
    "RR_Seasonality",
    "Recession_a_Seasonality",
    "AverageStorage",
    "RecessionParameters_1",
    "RecessionParameters_2",
    "First_Recession_Slope",
    "Mid_Recession_Slope",
    "EventRR_TotalRR_ratio",
    "VariabilityIndex",
    "BaseflowRecessionK",
    "BFI",
]  # df_imp["sig_name"].unique()

# sigs = [
#     "EventRR",
#     "TotalRR",
#     "RR_Seasonality",
#     "Recession_a_Seasonality",
#     "AverageStorage",
#     "RecessionParameters_b",
#     "RecessionParameters_T0",
#     "First_Recession_Slope",
#     "Mid_Recession_Slope",
#     "EventRR_TotalRR_ratio",
#     "VariabilityIndex",
#     "BaseflowRecessionK",
#     "BFI",
# ]

n_cols = 4  # Number of columns
n_rows = (len(sigs) + n_cols - 1) // n_cols  # Calculate number of rows needed


fig, axes = plt.subplots(
    nrows=n_rows,
    ncols=n_cols,
    figsize=(8 * n_cols, 10 * n_rows),
    constrained_layout=True,
)
axes = axes.flatten()  # Flatten the 2D array of axes to simplify indexing

# Loop over each signature
for i, sig in enumerate(sigs):
    sig_data = df_imp[df_imp["sig_name"] == sig].sort_values(
        by="%IncMSE", ascending=False
    )

    sns.barplot(
        data=sig_data,
        x="%IncMSE",
        y="predictor",
        palette=color_dict,
        ax=axes[i],
    )
    axes[i].set_title(sig, loc="left", fontsize=30)

# Hide unused subplots if there are any
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.show()


# %%
#########################################################
# Plot mean R2 per signature by cateogry
#########################################################

# Aggregate data by 'sig_name' to compute mean R-squared values
r2_summary = df_r2.groupby("sig_name")["r_squared"].mean().reset_index()
r2_summary.head()

sns.barplot(data=r2_summary, x="sig_name", y="r_squared", color="tab:grey")
# plt.title('RF Model Performance')
plt.ylabel(r"Mean $R^2$")
plt.xlabel("")
plt.ylim(0, 1)  # Adjust the y-axis limit to 0-1 as R-squared should be in this range
plt.xticks(rotation=90)
plt.show()
# %%
