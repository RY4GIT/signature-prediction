# %%
import os
import pandas as pd
import numpy as np
from tqdm import tqdm

# %% Config #########################################################
data_dir = r"D:\data"
out_dir = os.path.join(data_dir, "GAGES2_concat")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# %% Load streamflow data file names #########################################################
q_dir = os.path.join(data_dir, "GAGES2_streamflow", "all_gages2")
q_files = [f for f in os.listdir(q_dir) if f.endswith(".csv")]
print(f"Found {len(q_files)} q files")

# %% Load climate data #########################################################
gridmet_dir = os.path.join(data_dir, "GAGES2_gridMET")
precip_file = os.path.join(gridmet_dir, "pr_mm_gridmet_conus_gaged_1980_2020_mean.csv")
pet_file = os.path.join(gridmet_dir, "pet_mm_gridmet_conus_gaged_1980_2020_mean.csv")
tmax_file = os.path.join(
    gridmet_dir, "tmmx_degc_gridmet_conus_gaged_1980_2020_mean.csv"
)
tmin_file = os.path.join(
    gridmet_dir, "tmmn_degc_gridmet_conus_gaged_1980_2020_mean.csv"
)

print(f"Reading {precip_file}")
precip_df = pd.read_csv(precip_file)
print(f"Reading {pet_file}")
pet_df = pd.read_csv(pet_file)
print(f"Reading {tmax_file}")
tmax_df = pd.read_csv(tmax_file)
print(f"Reading {tmin_file}")
tmin_df = pd.read_csv(tmin_file)


# %% Set time index #########################################################
def set_time_index(df):
    df["date"] = pd.to_datetime(df["Date"])
    df.set_index("date", inplace=True)
    df.drop(columns=["Date"], inplace=True)
    return df


precip_df = set_time_index(precip_df)
pet_df = set_time_index(pet_df)
tmax_df = set_time_index(tmax_df)
tmin_df = set_time_index(tmin_df)

non_std_col_gages = []
# %% Process streamflow data #########################################################
for q_file in tqdm(
    q_files, desc="Processing streamflow data", total=len(q_files), leave=False
):
    # Get gauge ID
    nonfilled_gauge_id = q_file.split(".")[0]
    gauge_id = q_file.split(".")[0].zfill(8)
    print(f"Gauge ID: {gauge_id}")

    # Read streamflow data
    q_df = pd.read_csv(os.path.join(q_dir, q_file))
    q_df = set_time_index(q_df)

    # Get statistics about quality flag column
    # print(q_df["X_00060_00003_cd"].value_counts())

    # Get column names
    q_cfs_column_name = "X_00060_00003"
    if not q_cfs_column_name in q_df.columns:
        # Get first column that ends with _00060_00003
        q_cfs_column_name = [
            col for col in q_df.columns if col.endswith("_00060_00003")
        ][0]
        non_std_col_gages.append(gauge_id)
    q_qf_column_name = "X_00060_00003_cd"
    if not q_qf_column_name in q_df.columns:
        q_qf_column_name = [
            col for col in q_df.columns if col.endswith("_00060_00003_cd")
        ][0]

    # If the cd value is <, >, M, N, or U, then the data is suspect
    suspect_cds = ["<", ">", "M", "N", "U"]
    suspect_mask = q_df[q_qf_column_name].isin(suspect_cds)
    q_df["streamflow_mmd_before_qf"] = q_df["mmd"]
    q_df.loc[suspect_mask, "mmd"] = np.nan
    q_df.rename(columns={"mmd": "streamflow_mmd"}, inplace=True)
    q_df.index.name = "date"

    # Concat with climate data based on column name matching with gage id
    try:
        precip_df_gauge = (
            precip_df[nonfilled_gauge_id].copy().rename("total_precipitation_sum_mm")
        ).copy()
        pet_df_gauge = (
            pet_df[nonfilled_gauge_id].copy().rename("potential_evaporation_sum_mm")
        ).copy()
        tmax_df_gauge = tmax_df[nonfilled_gauge_id].copy()
        tmin_df_gauge = tmin_df[nonfilled_gauge_id].copy()
        tavg_df_gauge = (tmax_df_gauge + tmin_df_gauge) / 2
        tavg_df_gauge.rename("temperature_mean_degc", inplace=True)
    except KeyError:
        print(f"Gauge ID {nonfilled_gauge_id} not found in climate data")

    # Concat with climate data
    clim_df = (
        pd.merge(precip_df_gauge, q_df, on="date", how="left")
        .merge(pet_df_gauge, on="date", how="left")
        .merge(tavg_df_gauge, on="date", how="left")
    )

    # Clean up column names
    clim_df.rename(columns={q_cfs_column_name: "streamflow_cfs"}, inplace=True)
    clim_df.rename(columns={q_qf_column_name: "streamflow_qf"}, inplace=True)
    clim_df.drop(columns=["site_no"], inplace=True)

    # Save to file
    out_file = os.path.join(out_dir, f"gages2_{gauge_id}.csv")
    clim_df.to_csv(out_file, index=True)

    del precip_df_gauge, pet_df_gauge, tmax_df_gauge, tmin_df_gauge, tavg_df_gauge
    del clim_df

# %%
with open(os.path.join(out_dir, "non_std_col_gages.txt"), "w") as f:
    f.write(f"{non_std_col_gages}\n")
    f.close()

# %%
