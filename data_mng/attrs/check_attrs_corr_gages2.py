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
target_attrs_file = "attrs_gages2+climate_hammond.csv"
ref_file = "attrs_analysis.xlsx"
sheet_name = "gages2_basicsets"

df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
df_columns = df.columns.tolist()

attr_list = pd.read_excel(os.path.join(docs_dir, ref_file), sheet_name=sheet_name)

# %%
attr_list
# %%
missing_columns = [var for var in attr_list.VARIABLE_NAME if var not in df_columns]

# Display missing columns
if missing_columns:
    print("The following columns are not in the DataFrame:")
    print(missing_columns)
else:
    print("All columns are present in the DataFrame.")
# %%
df_filt = df[attr_list.VARIABLE_NAME].copy()
# Calculate spearman's correlation
corr_matrix = df_filt.corr(method="spearman")

fig_title = "Caravan attrs"
fig = plot_corr_heatmap(corr_matrix, fig_title)
fig.savefig(os.path.join(out_dir, "spearman_attrs_gages2.png"), dpi=600)
# %%
strong_correlations(corr_matrix)
strong_correlations

# %%___________________________________________________________________________
# %%___________________________________________________________________________
# Checking Caravan attributes (selected)
sheet_name = "gages2_final"

df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
df_columns = df.columns.tolist()

attr_list = pd.read_excel(os.path.join(docs_dir, ref_file), sheet_name=sheet_name)
# %%
missing_columns = [var for var in attr_list.VARIABLE_NAME if var not in df_columns]

# Display missing columns
if missing_columns:
    print("The following columns are not in the DataFrame:")
    print(missing_columns)
else:
    print("All columns are present in the DataFrame.")
# %%
df_filt = df[attr_list.VARIABLE_NAME].copy()
# Calculate spearman's correlation
corr_matrix = df_filt.corr(method="spearman")

fig_title = "Caravan attrs"
fig = plot_corr_heatmap(corr_matrix, fig_title)
fig.savefig(
    os.path.join(out_dir, "spearman_attrs_gages2+climate_selected.png"), dpi=600
)
# %%
strong_correlations(corr_matrix)
strong_correlations
# %%
