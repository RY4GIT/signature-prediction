# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

# %%
data_dir = r"D:\data"
gages2_dir = r"GAGES2_concat"
data_type = "csv"
attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan_attrs_gages2\attributes.csv"
out_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\caravan_datacheck"
)
# %%
attrs_geo = pd.read_csv(attrs_file)
attrs_geo.head()

# %%
gages2_q_dir = r"GAGES2_streamflow"
gages2_q_files = os.listdir(os.path.join(data_dir, gages2_q_dir, "all_gages2"))
gages2_q_files = [file for file in gages2_q_files if file.endswith(".csv")]
gauge_ids = [file.split(".")[0] for file in gages2_q_files]
gauge_ids = [gauge_id.zfill(8) for gauge_id in gauge_ids]
gauge_ids = list(set(gauge_ids))

# Create DataFrame with gauge_ids as strings and explicitly set dtype to prevent integer conversion
df = pd.DataFrame(gauge_ids, columns=["gauge_id"], dtype=str)
df.to_csv(os.path.join(data_dir, gages2_q_dir, "gages2_gauge_ids.csv"), index=False)
# %%
summary = []
failed_gauge_ids = []
# Create a tqdm wrapper around gauge_ids.iterrows()
for index, gauge_id in tqdm(enumerate(gauge_ids), total=len(gauge_ids)):
    try:
        gauge_id = gauge_id.zfill(8)
        # Construct the file path and load data
        file_path = os.path.join(
            data_dir,
            gages2_dir,
            f"gages2_{gauge_id}.{data_type}",
        )
        data = pd.read_csv(file_path)

        # Calculate required statistics
        start_date = data[data["streamflow_mmd"].notna()].date.iloc[0]
        end_date = data[data["streamflow_mmd"].notna()].date.iloc[-1]
        nan_count = data.streamflow_mmd.isna().sum()
        nan_fraction = nan_count / len(data.streamflow_mmd)

        data["date"] = pd.to_datetime(data["date"])
        data_subset = data[(data["date"] > start_date) & (data["date"] < end_date)]
        subset_nan_count = data_subset.streamflow_mmd.isna().sum()
        subset_nan_fraction = subset_nan_count / len(data_subset)
        Q95 = data.streamflow_mmd.quantile(0.95)

        # Append the results to the summary list
        summary.append(
            {
                "gauge_id": gauge_id,
                "start_date": start_date,
                "end_date": end_date,
                "nan_count": nan_count,
                "nan_fraction": nan_fraction,
                "subset_nan_fraction": subset_nan_fraction,
                "Q95": Q95,
            }
        )
    except Exception as e:
        print(e)
        summary.append(
            {
                "gauge_id": gauge_id,
                "start_date": "NaT",
                "end_date": "NaT",
                "nan_count": np.nan,
                "nan_fraction": np.nan,
                "subset_nan_fraction": np.nan,
                "Q95": np.nan,
            }
        )
        print(f"Error at {gauge_id}")
        failed_gauge_ids.append(gauge_id)

# Convert the summary list to a DataFrame
summary_df = pd.DataFrame(summary)

# Output the DataFrame to a CSV file
output_filename = os.path.join(out_dir, "gages2_summary.csv")
summary_df.to_csv(output_filename, index=False)
df = pd.DataFrame(failed_gauge_ids, columns=["gauge_id"], dtype=str)
df.to_csv(os.path.join(out_dir, "gages2_summary_failed.csv"), index=False)
print(f"Summary data has been saved to {output_filename}")

# %%
