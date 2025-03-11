# %%
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import seaborn as sns
import numpy as np
import textwrap

# %% #########################################################################
#
# LOAD ATTRIBUTES
#
##############################################################################
file_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_and_gages2+climate+morph+padcat.csv"
attrs = pd.read_csv(file_path)

# %%
caravan_attr_name = "area"
gages2_attr_name = "DRAIN_SQKM"

caravan_all = attrs[attrs[caravan_attr_name].notna()].copy()
gages2_subset = attrs[attrs[gages2_attr_name].notna()].copy()

caravan_gages_overlap = caravan_all.merge(
    gages2_subset, how="inner", left_on="gauge_id", right_on="gauge_id"
)

caravan_nsample = caravan_all.shape[0]
caravan_ref_nsample = caravan_all[caravan_all["CLASS"] == "Ref"].shape[0]
caravan_nonref_nsample = caravan_nsample - caravan_ref_nsample
gages2_nsample = gages2_subset.shape[0]
gages2_ref_nsample = gages2_subset[gages2_subset["CLASS"] == "Ref"].shape[0]
gages2_nonref_nsample = gages2_subset[gages2_subset["CLASS"] == "Non-ref"].shape[0]
caravan_gages2_overlap_nsample = caravan_gages_overlap.shape[0]

print(f"Caravan all: {caravan_nsample}")
print(
    f"Caravan ref gauges:{caravan_ref_nsample} ({caravan_ref_nsample / caravan_nsample * 100:.1f}%)"
)
print(
    f"Caravan non-ref gauges:{caravan_nonref_nsample} ({caravan_nonref_nsample / caravan_nsample * 100:.1f}%)"
)
print(
    f"GAGES2 subset: {gages2_nsample} ({caravan_gages2_overlap_nsample / caravan_nsample * 100:.1f}% of Caravan)"
)
print(
    f"GAGES2 subset, ref gauges: {gages2_ref_nsample} ({gages2_ref_nsample / gages2_nsample * 100:.1f}%)"
)
print(
    f"GAGES2 subset, non-ref gauges: {gages2_nonref_nsample} ({gages2_nonref_nsample / gages2_nsample * 100:.1f}%)"
)
print(
    f"Caravan-GAGES2 overlap: {caravan_gages2_overlap_nsample} (this should match with GAGES2 subset)"
)
# %%
prancevic_subset = attrs[
    attrs["p99_pave"].notna() & attrs[gages2_attr_name].notna()
].copy()
prancevic_subset_nsample = prancevic_subset.shape[0]
prancevic_subset_ref_nsample = prancevic_subset[
    prancevic_subset["CLASS"] == "Ref"
].shape[0]
prancevic_subset_nonref_nsample = (
    prancevic_subset_nsample - prancevic_subset_ref_nsample
)

print(f"Prancevic & GAGES2 subset: {prancevic_subset_nsample}")
print(
    f"Prancevic & GAGES2 ref gauges:{prancevic_subset_ref_nsample} ({prancevic_subset_ref_nsample / prancevic_subset_nsample * 100:.1f}%)"
)
print(
    f"Prancevic & GAGES2 non-ref gauges:{prancevic_subset_nonref_nsample} ({prancevic_subset_nonref_nsample / prancevic_subset_nsample * 100:.1f}%)"
)


# %%
def plot_hist(df, attr_name, title, bins=200, ax=None, xlim=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    df[attr_name][df["CLASS"] == "Ref"].hist(
        bins=bins, color="tab:blue", label="Ref", alpha=0.5, ax=ax
    )
    df[attr_name][df["CLASS"] != "Ref"].hist(
        bins=bins, color="tab:pink", label="Non-ref", alpha=0.5, ax=ax
    )
    ax.set_title(title)
    ax.set_xlabel(attr_name)
    ax.set_ylabel("Frequency")
    ax.legend()
    if xlim:
        ax.set_xlim(xlim)


# HYDRO_DISTURB_INDX	- Hydrologic "disturbance index" score,
# based on 7 variables: 1) MAJ_DDENS_2009, 2) WATER_WITHDR,
# 3) change in dam storage 1950-2009, 4) CANALS_PCT,
# 5) RAW_DIS_NEAREST_MAJ_NPDES, 6) ROADS_KM_SQ_KM, and 7) FRAGUN_BASIN.
# Low values = low anthropogenic hydrologic modification
# Plot histograms as a 1-by-2 subplot for specific attributes

# Plot histograms as a 1-by-2 subplot for specific attributes
attr_anthro_caravan = ["ppd_pk_sav", "gdp_ud_sav", "hdi_ix_sav"]
for attr in attr_anthro_caravan:
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    if attr == "gdp_ud_sav" or attr == "ppd_pk_sav":
        xlim = (caravan_all[attr].quantile(0.10), caravan_all[attr].quantile(0.90))
    else:
        xlim = None
    plot_hist(caravan_all, attr, f"Caravan ALL - {attr}", ax=axes[0], xlim=xlim)
    plot_hist(
        gages2_subset, attr, f"Caravan-GAGES2 subset - {attr}", ax=axes[1], xlim=xlim
    )
    plt.tight_layout()
    plt.show()

# Plot single histograms for other attributes
attr_anthro_gages2 = [
    "MAJ_DDENS_2009",
    "CANALS_PCT",
    "RAW_DIS_NEAREST_MAJ_NPDES",
    "ROADS_KM_SQ_KM",
    "FRAGUN_BASIN",
]
for attr in attr_anthro_gages2:
    if attr == "RAW_DIS_NEAREST_MAJ_NPDES":
        xlim = (0, 200)
    elif attr == "MAJ_DDENS_2009" or attr == "CANALS_PCT":
        xlim = (caravan_all[attr].quantile(0.10), caravan_all[attr].quantile(0.90))
    else:
        xlim = None
    plot_hist(gages2_subset, attr, f"Caravan-GAGES2 subset - {attr}", xlim=xlim)
# %%
