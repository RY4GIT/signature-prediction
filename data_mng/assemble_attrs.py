# %%
import pandas as pd
import os

# %%
###############################
subset_name = "hysets_test"
subset_caravan_name = "hysets"
derived_attrs_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs"
)
caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
###############################
# %%
# _____________________________________________________________________
# Load datasets
# Load spatial datasets
nwi_file = os.path.join(
    derived_attrs_dir, "NWI", f"conWetland_area_frac_{subset_name}.csv"
)
_nwi = pd.read_csv(nwi_file, index_col="gauge_id")
nwi = _nwi[["fresh", "lake", "other"]]  # TODO: reanme or manipulate this?
nwi.head()
# %%
giws_file = os.path.join(
    derived_attrs_dir, "GIWs", f"isoWetland_area_frac_{subset_name}.csv"
)
_giws = pd.read_csv(giws_file, index_col="gauge_id")
giws = _giws[["area_frac"]].rename(columns={"area_frac": "isowet_areafrac"})
giws.head()

# %%
geol_file_1 = os.path.join(
    derived_attrs_dir, "SGMC_Geology", f"age_weighted_{subset_name}.csv"
)
_geol1 = pd.read_csv(geol_file_1, index_col="gauge_id")
geol1 = _geol1[["av_age_w"]].rename(columns={"av_age_w": "geol_weighted_ave_age_ma"})
geol_file_2 = os.path.join(
    derived_attrs_dir, "SGMC_Geology", f"age_majorlith_{subset_name}.csv"
)
_geol2 = pd.read_csv(geol_file_2, index_col="gauge_id")
geol2 = _geol2[["major_lith", "av_age"]].rename(
    columns={"av_age": "geol_major_age_ma", "major_lith": "geol_major_lith"}
)
geol = geol1.join(geol2)
geol.head()
# %%
new_attrs = nwi.join(giws).join(geol)
new_attrs.fillna(
    {
        "isowet_areafrac": 0,
        "lake": 0,
        "fresh": 0,
        "other": 0,
    },
    inplace=True,
)
new_attrs["conwet_areafrac"] = (
    new_attrs["fresh"] + new_attrs["lake"] - new_attrs["isowet_areafrac"]
)

new_attrs["isowet_areafrac_masked"] = new_attrs["isowet_areafrac"].clip(lower=0)
new_attrs["conwet_areafrac"] = new_attrs["conwet_areafrac"].clip(lower=0)
new_attrs["lith_sed_carb"] = (
    new_attrs["geol_major_lith"] == "Sedimentary, carbonate"
).astype(int)
new_attrs["lith_sed_clast"] = (
    new_attrs["geol_major_lith"] == "Sedimentary, clastic"
).astype(int)
new_attrs["lith_ig_volc"] = (
    new_attrs["geol_major_lith"] == "Igneous, volcanic"
).astype(int)

new_attrs.head()

# %%
# _____________________________________________________________________
# Load original caravan attributes
attrs_cara_file = os.path.join(
    caravan_attrs_dir,
    subset_caravan_name,
    f"attributes_caravan_{subset_caravan_name}.csv",
)
attrs_cara = pd.read_csv(attrs_cara_file, index_col="gauge_id")
attrs_HA_file = os.path.join(
    caravan_attrs_dir,
    subset_caravan_name,
    f"attributes_hydroatlas_{subset_caravan_name}.csv",
)
attrs_HA = pd.read_csv(attrs_HA_file, index_col="gauge_id")
attrs_other_file = os.path.join(
    caravan_attrs_dir,
    subset_caravan_name,
    f"attributes_other_{subset_caravan_name}.csv",
)
attrs_other = pd.read_csv(attrs_other_file, index_col="gauge_id")
attrs_other.head()
caravan_attrs = attrs_other.join(attrs_cara).join(attrs_HA)
caravan_attrs.head()
# %%
# _____________________________________________________________________
# Join them all and output
attrs_all = caravan_attrs.join(new_attrs)
attrs_all.head()

attrs_all.to_csv(
    os.path.join(derived_attrs_dir, "assembled", f"attrs_{subset_name}.csv")
)
# %%
