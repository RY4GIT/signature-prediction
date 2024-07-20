# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
!pip install openpyxl
# %%
derived_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\assembled_RA"
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
        ax=ax
    )
    ax.set_title(f"Spearman Correlation ({fig_title})")  # Set the title using ax.set_title()
    fig.tight_layout()
    plt.show()  # Use plt.show() to display the plot
    return fig



def strong_correlations(corr_matrix, threshold=0.8):
    strong_pairs = []
    
    # Iterate through the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > threshold:
                strong_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_value))
    
    # Print the strong correlations
    for pair in strong_pairs:
        print(f"Correlation between {pair[0]} and {pair[1]}: {pair[2]:.2f}")
        
    return strong_pairs
# %%___________________________________________________________________________
# Checking Caravan attributes
target_attrs_file = "attrs_cam_hys.csv"
ref_file = "attrs_analysis.xlsx"
sheet_name = "basic_sets"

_df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
df = _df[_df.country == "United States of America"].copy()
df_columns = df.columns.tolist()

attr_list = pd.read_excel(
    os.path.join(derived_attrs_dir, ref_file), sheet_name=sheet_name
)
# %%
missing_columns = [var for var in attr_list.variable_name if var not in df_columns]

# Display missing columns
if missing_columns:
    print("The following columns are not in the DataFrame:")
    print(missing_columns)
else:
    print("All columns are present in the DataFrame.")
# %%
df_filt = df[attr_list.variable_name].copy()
# Calculate spearman's correlation
corr_matrix = df_filt.corr(method="spearman")

fig_title = "Caravan attrs"
fig = plot_corr_heatmap(corr_matrix, fig_title)
fig.savefig(os.path.join(out_dir, "spearman_attrs_caravan.png"), dpi=600)
# %%
strong_correlations(corr_matrix)
strong_correlations

# %%___________________________________________________________________________
# %%___________________________________________________________________________
# Checking Caravan attributes (selected)
sheet_name = "final"

_df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
df = _df[_df.country == "United States of America"].copy()
df_columns = df.columns.tolist()

attr_list = pd.read_excel(
    os.path.join(derived_attrs_dir, ref_file), sheet_name=sheet_name
)
# %%
missing_columns = [var for var in attr_list.variable_name if var not in df_columns]

# Display missing columns
if missing_columns:
    print("The following columns are not in the DataFrame:")
    print(missing_columns)
else:
    print("All columns are present in the DataFrame.")
# %%
df_filt = df[attr_list.variable_name].copy()
# Calculate spearman's correlation
corr_matrix = df_filt.corr(method="spearman")

fig_title = "Caravan attrs"
fig = plot_corr_heatmap(corr_matrix, fig_title)
fig.savefig(os.path.join(out_dir, "spearman_attrs_caravan_selected.png"), dpi=600)
# %%
strong_correlations(corr_matrix)
strong_correlations
# %%___________________________________________________________________________
# Checking attributes that Annie used
target_attrs_file = "attrs_camels_original.csv"


# target_attrs_file = "attrs_cam_hys.csv"
# fig_title = "CAMELS + Hysets, Caravan equiv attributes"

_df = pd.read_csv(
    os.path.join(derived_attrs_dir, target_attrs_file), index_col="gauge_id"
)
_df.columns
# %%
if target_attrs_file == "attrs_cam_hys.csv":
    selected_columns = [
        "frac_snow",
        "aridity",
        "low_prec_freq",
        "ele_mt_smn",
        "slp_dg_sav",
        "area",
        "for_pc_sse",
        "snd_pc_sav",
        "slt_pc_sav",
        "cly_pc_sav",
        "kar_pc_sse",
        "geol_major_age_ma",
        "isowet_areafrac",
    ]

    df = _df[selected_columns]
elif target_attrs_file == "attrs_camels_original.csv":
    selected_columns = [
        "p_seasonality",
        "frac_snow",
        "aridity",
        "low_prec_freq",
        "low_prec_dur",
        "elev_mean",
        "slope_mean",
        "area_gages2",
        "frac_forest",
        "root_depth_50",
        "root_depth_99",
        "soil_depth_statsgo",
        "max_water_content",
        "sand_frac",
        "silt_frac",
        "clay_frac",
        "other_frac",
        "carbonate_rocks_frac",
        "geol_porostiy",
        "geol_permeability",
        "geol_major_age_ma",
        "isowet_areafrac",
    ]

    df = _df[selected_columns]
else:
    df = _df

df.head()
# %%
# Calculate the Spearman correlation matrix
# Plotting the heatmap with the mask
fig_title = "Original CAMELS attrs (reprod. Annie's)"
corr_matrix = df.corr(method="spearman")
plot_corr_heatmap(corr_matrix, fig_title)


# %%
