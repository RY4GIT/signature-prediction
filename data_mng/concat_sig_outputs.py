# %%
import pandas as pd
import os

# %%
sig_outdir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"
)
out_dir = os.path.join(sig_outdir, "caravan_us_20240609_tunedparams")
hys_dir = "caravan_hysets_20240609_tunedparams"
camels_dir = "caravan_camels_20240609_tunedparams"

filename = "out_calc_All_custom.csv"
# %%
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# %%
hys = pd.read_csv(os.path.join(sig_outdir, hys_dir, filename))
print(len(hys), len(hys.columns))
camels = pd.read_csv(os.path.join(sig_outdir, camels_dir, filename))
print(len(camels), len(camels.columns))
# %%
cam_hys = pd.concat([camels, hys], axis=0).reset_index(drop=True)
print(len(cam_hys), len(cam_hys.columns))
# %%
cam_hys.to_csv(os.path.join(out_dir, filename), index=False)
# %%
