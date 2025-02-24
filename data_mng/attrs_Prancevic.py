# %%
import os
import pandas as pd

# %% ________________________________________
# Load geomophorlogy parameteres from Prancevic et al 2024
morph_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Prancevic_et_al_2025\science.ado2860_data_s2.csv"
morph_df = pd.read_csv(morph_file)
morph_df["gauge_num"] = morph_df["gauge_id"].astype(str).str.zfill(8)
morph_df.drop(columns=["gauge_id"], inplace=True)

# %% ________________________________________
# Load current attributes
assembled_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
ecoregion_ver = "epa"
# ecoregion_ver = "hammond"
caravan_epa_filename = f"attrs_cara_and_gages2+climate_{ecoregion_ver}.csv"

attrs_caravan_eco = pd.read_csv(os.path.join(assembled_attrs_dir, caravan_epa_filename))

# %%
attrs_caravan_eco["gauge_num"] = (
    attrs_caravan_eco["gauge_id"].str.split("_").str[-1].str.zfill(8)
)
attrs_caravan_eco.head()


# %%
attrs_caravan_eco
# %% ________________________________________
# Merge
merged_df = pd.merge(attrs_caravan_eco, morph_df, on="gauge_num", how="left")
# %%
merged_df.to_csv(
    os.path.join(
        assembled_attrs_dir, f"attrs_cara_and_gages2+climate_morph_{ecoregion_ver}.csv"
    ),
    index=False,
)

# %%
