# %%
import os
import pandas as pd

# Common path elements
base_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
version1 = r"data\Caravan1.2"
version2 = r"data\Caravan1.4"
file_name = r"attributes\hysets\attributes_other_hysets.csv"

# Construct file paths
path1 = os.path.join(base_path, version1, file_name)
path2 = os.path.join(base_path, version2, file_name)
output_path = os.path.join(
    base_path,
    r"out\caravan_datacheck",
    "hysets_ver_diff.csv",
)
# %%
df1 = pd.read_csv(path1)
print(f"Caravan 1.2 has {len(df1)} gauges")
df2 = pd.read_csv(path2)
print(f"Caravan 1.4 has {len(df2)} gauges ({len(df2)-len(df1)} more than 1.2)")

# Perform an outer merge on gauge_id
merged_df = pd.merge(df1, df2, on="gauge_id", how="outer", indicator=True)

# Filter out rows where gauge_id is only in one DataFrame
unique_df1 = merged_df[merged_df["_merge"] == "left_only"]
unique_df2 = merged_df[merged_df["_merge"] == "right_only"]

# Show results
print("\nUnique in ver 1.2")
print(unique_df1.head())
print("\nUnique in ver 1.4:")
print(unique_df2.head())


unique_df2.set_index("gauge_id", inplace=True)
unique_df2.to_csv(output_path)
# %%
