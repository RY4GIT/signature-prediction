# %%
import pandas as pd
import os

# %%
###############################
subset_name = "camels"
subset_caravan_name = "camels"
output_name = "camels_original"
derived_attrs_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs"
)
caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
camels_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\CAMELS\camels-20230412T1401Z"
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


# Function to format gauge_id
def format_gauge_id(gauge_id):
    return f"camels_{int(gauge_id):08d}"


if subset_name == "camels":
    # Apply the function to the gauge_id column
    new_attrs.index = new_attrs.index.map(format_gauge_id)

new_attrs.head()


# %%
# _____________________________________________________________________
# Load original caravan attributes

if not output_name == "camels_original":
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
else:
    attribute_types = ["hydro", "topo", "clim", "geol", "soil", "vege", "name"]
    _camels_attrs = {}
    # Loop through each attribute type and read the corresponding file
    for attr_type in attribute_types:
        file_path = os.path.join(camels_attrs_dir, f"camels_{attr_type}.txt")
        # Dynamically create variable names and assign dataframes to them
        _camels_attrs[attr_type] = pd.read_csv(file_path, sep=";", index_col="gauge_id")

    # Initialize a variable to hold the joined dataframe
    camels_attrs = None
    # Merge all dataframes on 'gauge_id'
    for df in _camels_attrs.values():
        if camels_attrs is None:
            camels_attrs = df
        else:
            camels_attrs = camels_attrs.join(df)

    camels_attrs.index = camels_attrs.index.map(format_gauge_id)
    camels_attrs.head()

    # _____________________________________________________________________
    # Join them all and output
    attrs_all = camels_attrs.join(new_attrs)
    attrs_all.head()
# %%

attrs_all.to_csv(
    os.path.join(derived_attrs_dir, "assembled_RA", f"attrs_{output_name}.csv")
)
# %%

# # %%
# path1 = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20240530_defaultparams\out_calc_McMillan_Groundwater.csv"
# path2 = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20240530_defaultparams\out_calc_McMillan_OverlandFlow.csv"
# sig_gw_df = pd.read_csv(path1, index_col="gauge_id")
# sig_of_df = pd.read_csv(path2, index_col="gauge_id")
# # %%
# sig_all = sig_gw_df.join(sig_of_df)
# sig_all.head()
# # %%
# print(sig_all.columns)
# # %%
# sig_all.to_csv(r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20240530_defaultparams\out_calc_All.csv")
# # %%
