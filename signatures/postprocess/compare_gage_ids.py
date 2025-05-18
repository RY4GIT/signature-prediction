# %%
import pandas as pd
import os

# Define the shared drive path and output directory
shared_drive = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
sig_outdir = os.path.join(shared_drive, "out", "signatures")
caravan_dir = "caravan_us_20250223_withWu"
out_dir = os.path.join(sig_outdir, caravan_dir)

# File paths
file1 = os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area_gages2subset.csv")
file2 = os.path.join(out_dir, "out_calc_All_custom_filt_qc_snow_area_subset_gages2.csv")

# Read the CSV files
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Get the sets of gage IDs from each file
gages1 = set(df1["gauge_id"])
gages2 = set(df2["gauge_id"])

# Find gages that are in file1 but not in file2
only_in_file1 = gages1 - gages2
print(f"\nGages only in {os.path.basename(file1)}:")
print(f"Count: {len(only_in_file1)}")
print(sorted(list(only_in_file1)))

# Find gages that are in file2 but not in file1
only_in_file2 = gages2 - gages1
print(f"\nGages only in {os.path.basename(file2)}:")
print(f"Count: {len(only_in_file2)}")
print(sorted(list(only_in_file2)))

# Print summary
print(f"\nSummary:")
print(f"Total gages in file1: {len(gages1)}")
print(f"Total gages in file2: {len(gages2)}")
print(f"Number of gages only in file1: {len(only_in_file1)}")
print(f"Number of gages only in file2: {len(only_in_file2)}")
print(f"Number of common gages: {len(gages1.intersection(gages2))}")

# %%
