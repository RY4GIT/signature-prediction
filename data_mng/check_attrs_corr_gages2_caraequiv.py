# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# %%
derived_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
docs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\docs"
out_dir = os.path.join(derived_attrs_dir, "figs")


def plot_corr_heatmap(corr_matrix, fig_title):
    # Create a mask to hide the upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    # Plot
    fig, ax = plt.subplots(figsize=(20, 20))  # Use plt.subplots() to create fig and ax
    sns.heatmap(
        corr_matrix,
        annot=True,
        annot_kws={"size": 8},
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        mask=mask,
        ax=ax,
    )
    ax.set_title(
        f"Spearman Correlation ({fig_title})"
    )  # Set the title using ax.set_title()
    fig.tight_layout()
    plt.show()  # Use plt.show() to display the plot
    return fig


def strong_correlations(corr_matrix, threshold=0.8):
    strong_pairs = []

    # Iterate through the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > threshold:
                strong_pairs.append(
                    (corr_matrix.columns[i], corr_matrix.columns[j], corr_value)
                )

    # Print the strong correlations
    for pair in strong_pairs:
        print(f"Correlation between {pair[0]} and {pair[1]}: {pair[2]:.2f}")

    return strong_pairs


# %%___________________________________________________________________________
# Checking Caravan attributes
target_attrs_file = "attrs_cara_and_gages2+climate+morph+padcat.csv"
ref_file = "attrs_analysis.xlsx"
sheet_name = "gages2_basicsets"

df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
df_columns = df.columns.tolist()

attr_list = [
    "ELEV_MEAN_M_BASIN",
    "DRAIN_SQKM",
    "SLOPE_PCT",
    "FORESTNLCD06",
    "CROPSNLCD06",
    "PASTURENLCD06",
    "PCT_IRRIG_AG",
    "SNOWICENLCD06",
    "PADCAT1_AND_2",
    "isowet_areafrac",
    "CLAYAVE",
    "SILTAVE",
    "OMAVE",
    "kar_pc_sse",
    "geol_weighted_ave_age_ma",
    "PDEN_2000_BLOCK",
    "gdp_ud_sav",
    # "DEVNLCD06",
    "P_mm_day",
    "PET_mm_day",
    "ARIDITY_GAGES2",
    "SNOW_PCT_PRECIP",
    "PRECIP_SEAS_IND",
    "high_prec_freq",
    "low_prec_freq",
    "low_prec_dur",
    "ASPECT_NORTHNESS",
    "ASPECT_EASTNESS",
    # "HYDRO_DISTURB_INDX",
    # "MAJ_DDENS_2009",
    "FRAGUN_BASIN",
]

# %%
attr_list
# %%
missing_columns = [var for var in attr_list if var not in df_columns]

# Display missing columns
if missing_columns:
    print("The following columns are not in the DataFrame:")
    print(missing_columns)
else:
    print("All columns are present in the DataFrame.")
# %%
df_filt = df[attr_list].copy()
# Calculate spearman's correlation
corr_matrix = df_filt.corr(method="spearman")

fig_title = "Caravan attrs"
fig = plot_corr_heatmap(corr_matrix, fig_title)
fig.savefig(os.path.join(out_dir, "spearman_attrs_gages2.png"), dpi=600)
# %%
strong_correlations(corr_matrix)
strong_correlations

# %%
