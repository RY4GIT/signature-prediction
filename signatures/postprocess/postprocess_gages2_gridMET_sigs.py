# %%
import os
import pandas as pd
import numpy as np

# %%
sig_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"

gridmet_sigs_dir = "gages2_20250608"
caravan_sigs_dir = "caravan_us_20250525"

gridmet_sigs_file = os.path.join(sig_dir, gridmet_sigs_dir, "out_calc_All_custom.csv")
caravan_sigs_file = os.path.join(
    sig_dir, caravan_sigs_dir, "out_calc_All_custom_filt_qc_snow_area.csv"
)

# %%
gridmet_sigs = pd.read_csv(gridmet_sigs_file)
gridmet_sigs["gauge_id"] = gridmet_sigs["gauge_id"].astype(str)
caravan_sigs = pd.read_csv(caravan_sigs_file)
caravan_sigs["gauge_num"] = caravan_sigs["gauge_num"].astype(str).str.zfill(8)
