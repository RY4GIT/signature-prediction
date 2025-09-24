# %%
import pandas as pd
import os

# %%
camels_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_camels.csv"
camels_attrs = pd.read_csv(camels_attrs_file)
camels_attrs["gauge_num"] = (
    camels_attrs["gauge_id"].astype(str).str.split("_").str[-1].str.zfill(8)
)
print(len(camels_attrs))
# %%
camels_attrs.head()

# %%

# %%
gages2_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\GAGES2\GAGES_II_attrs\gagesII_sept30_2011_concat.csv"
gages2_attrs = pd.read_csv(gages2_attrs_file)
gages2_attrs["gauge_num"] = gages2_attrs["STAID"].astype(str).str.zfill(8)
print(len(gages2_attrs))

# %%
gages2_attrs.head()
# %%
camels_gages2_overlap = camels_attrs.merge(
    gages2_attrs, left_on="gauge_num", right_on="gauge_num", how="inner"
)
camels_gages2_overlap.head()
print(len(camels_gages2_overlap))
# %%
hysets_attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_hysets.csv"
hysets_attrs = pd.read_csv(hysets_attrs_file)
hysets_attrs["gauge_num"] = (
    hysets_attrs["gauge_id"].astype(str).str.split("_").str[-1].str.zfill(8)
)
print(len(hysets_attrs))
# %%
hysets_attrs.head()
# %%
hysets_camels_overlap = hysets_attrs.merge(
    camels_attrs, left_on="gauge_num", right_on="gauge_num", how="inner"
)
hysets_camels_overlap.head()
print(len(hysets_camels_overlap))
# %%
671 / 2
# %%
