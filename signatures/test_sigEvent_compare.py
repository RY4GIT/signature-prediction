# %%
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %%
hourly_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\test_hourlyCAMELS_v2_20250730\out_sigEvent.csv"
# hourly_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\test_hourlyCAMELS_20250728\out_sigEvent.csv"
# hourly_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\test_hourlyCAMELS_defaultParam20250728\out_sigEvent.csv"
df_hourly = pd.read_csv(hourly_path, index_col="gauge_id")

daily_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\signatures\caravan_camels_20250525\out_calc_All_custom.csv"
df_daily = pd.read_csv(daily_path, index_col="gauge_id")

attrs_path = r"D:\data\Caravan1.5\attributes\camels\attributes_other_camels.csv"
df_attrs = pd.read_csv(attrs_path, index_col="gauge_id")

# %%
# Merge the dataframes
df_merged = pd.merge(
    df_hourly, df_daily, on="gauge_id", how="inner", suffixes=("_hourly", "_daily")
)
df_merged = pd.merge(df_merged, df_attrs, on="gauge_id", how="inner")

df_merged.head()
# %%
# Compare the two dataframes
# Plot the scatter plot for "R_Pint_RC" and "R_Pvol_RC"
fig, ax = plt.subplots(1, 2, figsize=(9, 4))

varname = "R_Pvol_RC"
i = 1
df_clean = df_merged.dropna(subset=[f"{varname}_hourly", f"{varname}_daily"])
ax[i].scatter(df_clean[f"{varname}_hourly"], df_clean[f"{varname}_daily"], alpha=0.5)
ax[i].set_xlabel("Hourly CAMELS")
ax[i].set_ylabel("Daily CAMELS")
ax[i].set_title(f"{varname}")
ax[i].set_xlim(0, 1)
ax[i].set_ylim(0, 1)
ax[i].grid(True)
ax[i].axline((0, 0), (1, 1), color="grey", linestyle="--")
# Add the fitted line to the data
z = np.polyfit(df_clean[f"{varname}_hourly"], df_clean[f"{varname}_daily"], 1)
p = np.poly1d(z)
ax[i].plot(
    df_clean[f"{varname}_hourly"],
    p(df_clean[f"{varname}_hourly"]),
    "-",
    color="royalblue",
    alpha=0.5,
)

varname = "R_Pint_RC"
i = 0
ax[i].scatter(df_clean[f"{varname}_hourly"], df_clean[f"{varname}_daily"], alpha=0.5)
ax[i].set_xlabel("Hourly CAMELS")
ax[i].set_ylabel("Daily CAMELS")
ax[i].set_title(f"{varname}")
ax[i].set_xlim(0, 1)
ax[i].set_ylim(0, 1)
ax[i].grid(True)
ax[i].axline((0, 0), (1, 1), color="grey", linestyle="--")
# Add the fitted line to the data
z = np.polyfit(df_clean[f"{varname}_hourly"], df_clean[f"{varname}_daily"], 1)
p = np.poly1d(z)
ax[i].plot(
    df_clean[f"{varname}_hourly"],
    p(df_clean[f"{varname}_hourly"]),
    "-",
    color="royalblue",
    alpha=0.5,
)

# %%
df_clean["diff_Pint_Pvol_daily"] = (
    df_clean["R_Pint_RC_daily"] - df_clean["R_Pvol_RC_daily"]
)
df_clean["diff_Pint_Pvol_hourly"] = (
    df_clean["R_Pint_RC_hourly"] - df_clean["R_Pvol_RC_hourly"]
)

# %% Plot in the map
fig, ax = plt.subplots(
    3, 2, figsize=(15, 10), subplot_kw={"projection": ccrs.PlateCarree()}
)
land = cfeature.NaturalEarthFeature(
    category="physical", name="land", scale="110m", facecolor="lightgrey", zorder=0
)
ax = ax.flatten()


plot_items = {
    "R_Pint_RC_daily": {
        "title": "R_Pint_RC (daily)",
        "colorbar": "viridis",
    },
    "R_Pvol_RC_daily": {
        "title": "R_Pvol_RC (daily)",
        "colorbar": "viridis",
    },
    "R_Pint_RC_hourly": {
        "title": "R_Pint_RC (hourly)",
        "colorbar": "viridis",
    },
    "R_Pvol_RC_hourly": {
        "title": "R_Pvol_RC (hourly)",
        "colorbar": "viridis",
    },
    "diff_Pint_Pvol_daily": {
        "title": "R_Pint_RC - R_Pvol_RC (daily)",
        "colorbar": "RdBu_r",
    },
    "diff_Pint_Pvol_hourly": {
        "title": "R_Pint_RC - R_Pvol_RC (hourly)",
        "colorbar": "Reds",
    },
}
for i, (varname, item) in enumerate(plot_items.items()):
    if "diff_Pint_Pvol_daily" in varname:
        norm = plt.Normalize(-0.1, 0.1)
    elif "diff_Pint_Pvol_hourly" in varname:
        norm = plt.Normalize(-0.2, 0.0)
    else:
        norm = plt.Normalize(-0.3, 0.8)
    ax[i].add_feature(land)
    ax[i].scatter(
        df_clean["gauge_lon"],
        df_clean["gauge_lat"],
        c=df_clean[varname],
        alpha=0.5,
        transform=ccrs.PlateCarree(),
        norm=norm,
        cmap=item["colorbar"],
    )
    ax[i].set_title(item["title"])
    cbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=item["colorbar"]),
        ax=ax[i],
        shrink=0.5,
    )

fig.tight_layout()


# %%
