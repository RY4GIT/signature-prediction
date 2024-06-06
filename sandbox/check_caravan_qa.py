# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# %%
data_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data"
caravan_dir = r"Caravan1.4"
attributes_dir = "attributes"
timeseries_dir = r"timeseries"
data_type = "csv"
caravan_data = "hysets"
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\caravan_datacheck"

# %%
# attrs_cara = pd.read_csv(os.path.join(data_dir, caravan_dir, attributes_dir, caravan_data, f"attributes_caravan_hysets.{data_type}"))
# attrs_cara_names = attrs_cara.columns.to_list()
# attrs_HA = pd.read_csv(os.path.join(data_dir, caravan_dir, attributes_dir, caravan_data, f"attributes_hydroatlas_hysets.{data_type}"))
# attrs_HA_names = attrs_HA.columns.to_list()
attrs_geo = pd.read_csv(os.path.join(data_dir, caravan_dir, attributes_dir, caravan_data, f"attributes_other_hysets.{data_type}"))
attrs_geo_names = attrs_geo.columns.to_list()
attrs_geo.head()

# %%
us_gauges = attrs_geo[attrs_geo["country"]=="United States of America"].copy()
# print(us_gauges.describe())
# us_gauges.head()
# Loop through each gauge in us_gauges
summary = []
from tqdm import tqdm

# Create a tqdm wrapper around us_gauges.iterrows()
for index, us_gauge in tqdm(us_gauges.iterrows(), total=len(us_gauges)):
    try:
        # Construct the file path and load data
        file_path = os.path.join(data_dir, caravan_dir, timeseries_dir, data_type, caravan_data, f"{us_gauge.gauge_id}.{data_type}")
        data = pd.read_csv(file_path)
        
        # Calculate required statistics
        start_date = data[data['streamflow'].notna()].date.iloc[0]
        end_date = data[data['streamflow'].notna()].date.iloc[-1]
        nan_count = data.streamflow.isna().sum()
        nan_fraction = nan_count / len(data.streamflow)

        data["date"] = pd.to_datetime(data["date"])
        data_subset = data[(data["date"] > start_date) & (data["date"] < end_date)]
        subset_nan_count = data_subset.streamflow.isna().sum()
        subset_nan_fraction = subset_nan_count / len(data_subset)
        
        # Append the results to the summary list
        summary.append({
            "gauge_id": us_gauge.gauge_id,
            "start_date": start_date,
            "end_date": end_date,
            "nan_count": nan_count,
            "nan_fraction": nan_fraction,
            "subset_nan_fraction": subset_nan_fraction
        })
    except Exception as e:
        print(e)
        summary.append({
            "gauge_id": us_gauge.gauge_id,
            "start_date": "NaT",
            "end_date": "NaT",
            "nan_count": np.nan,
            "nan_fraction": np.nan,
            "subset_nan_fraction": subset_nan_fraction
        })
        print(f"Error at {us_gauge.gauge_id}")

# Convert the summary list to a DataFrame
summary_df = pd.DataFrame(summary)

# Output the DataFrame to a CSV file
output_filename = os.path.join(out_dir, f"{caravan_data}_summary.csv")
summary_df.to_csv(output_filename, index=False)

print(f"Summary data has been saved to {output_filename}")

# %%
