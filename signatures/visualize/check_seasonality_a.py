# %%
import pandas as pd

# %%
sig_file = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures"
    r"\caravan_camels_20260716\out_calc_All_custom_shortlist.csv"
)
df = pd.read_csv(sig_file)

# %%
col = "Recession_a_Seasonality"
high = df.loc[df[col] > 15, ["gauge_id", col]].sort_values(col, ascending=False)

print(f"Loaded {len(df)} gauges")
print(f"{col} > 15: {len(high)} gauges")
print(high.to_string(index=False))
