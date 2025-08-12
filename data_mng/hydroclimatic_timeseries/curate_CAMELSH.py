# %%
import pandas as pd
import os
import xarray as xr
import matplotlib.pyplot as plt
from tqdm import tqdm

# %%
data_dir = r"D:\data\CAMELSH"
obs_dir = os.path.join(data_dir, "timeseries")
nonobs_dir = os.path.join(data_dir, "timeseries_nonobs")
out_dir = os.path.join(data_dir, "timeseries_max_hourly_frac")
os.makedirs(out_dir, exist_ok=True)
# %% Get the list of files in the obs_dir ending with .nc
for target_dir in [obs_dir, nonobs_dir]:
    ts_files = sorted(
        [
            os.path.join(target_dir, entry)
            for entry in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, entry)) and entry.endswith(".nc")
        ]
    )
    print(f"Number of files in {target_dir}: {len(ts_files)}")

    for ts_file in tqdm(ts_files):
        try:
            # Open the dataset
            ds = xr.open_dataset(ts_file)

            # Calculate rainfall statistics
            rain_hourly = ds.Rainf.to_dataframe()
            rain_hourly = rain_hourly.sort_index()
            daily_sum = rain_hourly.resample("D").sum(min_count=24)
            daily_sum.columns = ["daily_precipitation"]
            daily_max = rain_hourly.resample("D").max(min_count=24)
            daily_max.columns = ["max_hourly_precipitation"]

            dailysummax = pd.concat([daily_max, daily_sum], axis=1)

            # Get the max-hourly fraction
            max_hourly_frac = (
                dailysummax["max_hourly_precipitation"]
                / dailysummax["daily_precipitation"]
            ).rename("max_hourly_frac")

            # Set fraction to 0 for days with zero daily precipitation and fill NaNs with 0
            max_hourly_frac = max_hourly_frac.mask(
                dailysummax["daily_precipitation"] == 0, 0
            ).fillna(0)

            # Save the max_hourly_frac to a csv file
            guage_id = ts_file.split("\\")[-1].split(".")[0]
            max_hourly_frac.to_csv(os.path.join(out_dir, f"{guage_id}.csv"))

        except Exception as e:
            print(f"Error opening {ts_file}: {e}")
            continue
