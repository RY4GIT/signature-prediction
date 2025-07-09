# %% Generate peudo attributes file for SHAP testing

import pandas as pd
import os

# %%
data_dir = "G:/Shared drives/Signatures -- large scale/baseflow/RAraki/data/derived_attrs/assembled_RA"

# %%
attrs = pd.read_csv(
    os.path.join(data_dir, "attrs_cara_gages2_etc_20250517+cluster.csv")
)

# %%
attrs["geol_weighted_ave_age_ma_copy"] = attrs["geol_weighted_ave_age_ma"].copy()


attrs.to_csv(
    os.path.join(data_dir, "attrs_cara_gages2_etc_20250517+cluster_copy_for_shap.csv"),
    index=False,
)

# %%
