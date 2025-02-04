# %%
import pandas as pd
import netCDF4
import os
import xarray as xr
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
# %% To check NC file
# surface_melt_nc = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\surface_water_input_Hammond\melt_surface_water_input_WYs_1991_2023.nc"
# ds = xr.open_dataset(surface_melt_nc)


# %%
def load_surface_water_input_data(surface_dir, filename, nrows=10):
    """
    Load surface water input data from a CSV file.

    Parameters:
        surface_dir (str): Directory where the CSV file is located.
        filename (str): Name of the CSV file.
        nrows (int): Number of rows to read from the CSV file.

    Returns:
        df (pd.DataFrame): DataFrame containing the loaded data.
        gauge_ids (pd.Index): Column names (gauge IDs) from the DataFrame.
        time_idx (pd.Series): Time index from the CSV file.
    """
    # Construct the full file path
    filepath = os.path.join(surface_dir, filename)

    # Load the data into a DataFrame
    df = pd.read_csv(filepath, nrows=nrows, index_col=0)

    # Convert the index to datetime
    df.index = pd.to_datetime(df.index, format="%Y.%m.%d")

    # Extract gauge IDs (column names)
    gauge_ids = df.columns

    # Load the time index (first column) from the CSV file
    time_idx = pd.read_csv(filepath, usecols=[0])

    return gauge_ids, time_idx


# %% #########################################################################
# Config
#############################################################################
surface_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\surface_water_input_Hammond"
surface_melt_csv = "melt_surface_water_input_WYs_1991_2023.csv"
surface_mix_csv = "mix_surface_water_input_WYs_1991_2023.csv"
surface_rain_csv = "rain_surface_water_input_WYs_1991_2023.csv"
#############################################################################

# %% _______________________________________________________________________
# Load data
# Load data for "melt"
gauge_ids_melt, time_idx_melt = load_surface_water_input_data(
    surface_dir, surface_melt_csv
)

# Load data for "mix"
gauge_ids_mix, time_idx_mix = load_surface_water_input_data(
    surface_dir, surface_mix_csv
)

# Load data for "rain"
gauge_ids_rain, time_idx_rain = load_surface_water_input_data(
    surface_dir, surface_rain_csv
)

# %% _______________________________________________________________________
# Compare gaugas and time index from different datasets
if list(gauge_ids_melt) == list(gauge_ids_mix) == list(gauge_ids_rain):
    print("All gauge IDs are the same and in the same order.")
else:
    print("Gauge IDs are not the same or are in a different order.")

# Directly compare the lists (order matters)
if list(time_idx_melt) == list(time_idx_mix) == list(time_idx_rain):
    print("All time index are the same and in the same order.")
else:
    print("Time index are not the same or are in a different order.")

# %% _______________________________________________________________________
# Load and separate each gauge data
# Specify the columns you want to load
gauge_ids = gauge_ids_melt
time_idx = time_idx_melt

# Create output directory if it doesn't exist
out_dir = os.path.join(surface_dir, "preprocessed")
os.makedirs(out_dir, exist_ok=True)


# Loop through each gauge ID with a progress bar
for gauge_to_load in tqdm(gauge_ids, desc="Processing gauges"):
    # %% _______________________________________________________________________
    # Read the CSV file and load only the specified columns

    # Melt data
    melt_data = pd.read_csv(
        os.path.join(surface_dir, surface_melt_csv), usecols=[gauge_to_load]
    )  # , index_col=0)
    melt_data.rename(columns={gauge_to_load: "melt_mm"}, inplace=True)  # %%

    # Mixed data
    mix_data = pd.read_csv(
        os.path.join(surface_dir, surface_mix_csv), usecols=[gauge_to_load]
    )  # , index_col=0)
    mix_data.rename(columns={gauge_to_load: "mix_mm"}, inplace=True)  # %%

    # Rain data
    rain_data = pd.read_csv(
        os.path.join(surface_dir, surface_rain_csv), usecols=[gauge_to_load]
    )  # , index_col=0)
    rain_data.rename(columns={gauge_to_load: "rain_mm"}, inplace=True)  # %%

    # _______________________________________________________________________
    # Concat all data and format
    df = pd.concat([time_idx, melt_data, mix_data, rain_data], axis=1)

    df["date"] = pd.to_datetime(df["Unnamed: 0"], format="%Y.%m.%d")

    # _______________________________________________________________________
    # Output
    out_filename = f"gages2_{gauge_to_load.zfill(8)}.csv"
    df[["date", "melt_mm", "mix_mm", "rain_mm"]].to_csv(
        os.path.join(out_dir, out_filename), index=False
    )
