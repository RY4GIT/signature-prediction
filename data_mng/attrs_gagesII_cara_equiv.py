# %%
import os
import pandas as pd
import matplotlib.pyplot as plt

# %%
attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA"
filename = "attrs_cara_and_gages2+climate+morph.csv"


# %%
attrs = pd.read_csv(os.path.join(attrs_dir, filename))
attrs.head()

# %% Check if geomorphology attribute are actually contributing, or maybe because of sample size
print(f"GAGES 2 attrs sample: {attrs['CANALS_PCT'].notna().sum()}")
print(
    f"GAGES 2 + morph attrs sample: {attrs[['CANALS_PCT', 'p99_pave']].notna().all(axis=1).sum()}"
)

# %% ####################################
# PROTECTED AREA PERCENTAGE
########################################
#  Get protected area precent basin based on GAGES II datasets
attrs["PADCAT1_AND_2"] = attrs["PADCAT1_PCT_BASIN"] + attrs["PADCAT2_PCT_BASIN"]

# Create a scatter plot between pac_pc_sse and PADCAT1_AND_2
plt.figure(figsize=(10, 6))
plt.scatter(attrs["pac_pc_sse"], attrs["PADCAT1_AND_2"], alpha=0.5)
plt.xlabel("pac_pc_sse")
plt.ylabel("PADCAT1_AND_2")
plt.title("Scatter plot between pac_pc_sse and PADCAT1_AND_2")
plt.show()


# %% ####################################
# CLIMATE EQUIVALENTs
########################################
attrs["PET_mm_day"] = attrs["PET"] / 365  # mm/year to mm/day
attrs["P_mm_day"] = (attrs["PPTAVG_BASIN"] * 10) / 365  # cm/year to mm/day
attrs["ARIDITY_GAGES2"] = attrs["PET"] / (
    attrs["PPTAVG_BASIN"] * 10
)  # PET/P, convert both in mm/year

attrs["ARIDITY_GAGES2"].hist(bins=100)


# %% ####################################
# CLIMATE EQUIVALENTs
########################################

# %%
attrs.to_csv(
    os.path.join(attrs_dir, "attrs_cara_and_gages2+climate+morph+padcat.csv"),
    index=False,
)
# %%
