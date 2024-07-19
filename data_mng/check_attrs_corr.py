# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os


# %%
# Load dataset
derived_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs\assembled_RA"
target_attrs_file = "attrs_camels_original.csv"
fig_title = "Original CAMELS attrs (reprod. Annie's)"

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
corr_matrix = df.corr(method="spearman")

# Create a mask to hide the upper triangle
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

# Plotting the heatmap with the mask
plt.figure(figsize=(10, 10))
sns.heatmap(
    corr_matrix,
    annot=True,
    annot_kws={"size": 8},
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    mask=mask,
)
plt.title(f"Spearman Correlation\n({fig_title})")
plt.tight_layout()
plt.show()

# %%
