# %% Checking IE/SE signatures performance under snow

import pandas as pd
import os

# %% ######################
# PREPARATION
##########################

# ____________________________________________________________________________________
# Config
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_us_20240609_tunedparams"

df_sigs = pd.read_csv(
    os.path.join(out_dir, "out_calc_All_custom_filt.csv"), index_col="gauge_id"
)

df_sigs.head()

# %%
df_sigs.columns
# %%
df_sigs["IE_thresh_signif"].hist(bins=30, range=(0, 0.0001), edgecolor="black")

# %%
# Define West Coast longitude range (adjust if needed)
west_coast_lon_range = (-125, -115)

# Filter data
west_coast_gauges = df_sigs[
    (df_sigs["IE_thresh_signif"] < 0.0001)
    & (df_sigs["gauge_lon"].between(*west_coast_lon_range))
]

# %%
len(west_coast_gauges)
print(west_coast_gauges.head())
# %%
out_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\temp"
)
select_columns = [
    "IE_thresh",
    "SE_thresh",
    "IE_thresh_signif",
    "SE_thresh_signif",
    "Storage_thresh",
    "SE_slope",
    "gauge_lat",
    "gauge_lon",
    "gauge_name",
    "area",
]
west_coast_gauges[select_columns].to_csv(os.path.join(out_dir, "IESE_westcoast.csv"))

# %%
