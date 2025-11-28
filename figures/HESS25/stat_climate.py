# %%
import os
import pandas as pd


# %% Load attribute file
attrs_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv"
attrs = pd.read_csv(attrs_file)
attrs.head()

# %% Get statistics on East and South clusters on Elevation, Temperature, and Precipitation
east_south_clusters = [5, 1]
east_south_attrs = attrs[attrs["cluster"].isin(east_south_clusters)]
east_south_attrs.head()

# %%
print("--------------------------------")
print("Elevation")
print(east_south_attrs["ELEV_MEAN_M_BASIN"].describe())
print(
    "10th percentile of Elevation", east_south_attrs["ELEV_MEAN_M_BASIN"].quantile(0.1)
)
print(
    "90th percentile of Elevation", east_south_attrs["ELEV_MEAN_M_BASIN"].quantile(0.9)
)

# %%
print("--------------------------------")
print("Temperature")
print(east_south_attrs["T_AVG_BASIN"].describe())
print("10th percentile of Temperature", east_south_attrs["T_AVG_BASIN"].quantile(0.1))
print("90th percentile of Temperature", east_south_attrs["T_AVG_BASIN"].quantile(0.9))
# %%
print("--------------------------------")
print("Precipitation")
east_south_attrs["P_mm_yr"] = east_south_attrs["P_mm_day"] * 365
print(east_south_attrs["P_mm_yr"].describe())
print("10th percentile of Precipitation", east_south_attrs["P_mm_yr"].quantile(0.1))
print("90th percentile of Precipitation", east_south_attrs["P_mm_yr"].quantile(0.9))

# %% Get staitsitc on Midwest and Central cluster
midwest_central_clusters = [0]
midwest_central_attrs = attrs[attrs["cluster"].isin(midwest_central_clusters)]
midwest_central_attrs.head()

# %%
print("--------------------------------")
print("Elevation")
print(midwest_central_attrs["ELEV_MEAN_M_BASIN"].describe())
print(
    "10th percentile of Elevation",
    midwest_central_attrs["ELEV_MEAN_M_BASIN"].quantile(0.1),
)
print(
    "90th percentile of Elevation",
    midwest_central_attrs["ELEV_MEAN_M_BASIN"].quantile(0.9),
)
# %%
print("--------------------------------")
print("Temperature")
print(midwest_central_attrs["T_AVG_BASIN"].describe())
print(
    "10th percentile of Temperature", midwest_central_attrs["T_AVG_BASIN"].quantile(0.1)
)
print(
    "90th percentile of Temperature", midwest_central_attrs["T_AVG_BASIN"].quantile(0.9)
)
# %%
print("--------------------------------")
print("Precipitation")
midwest_central_attrs["P_mm_yr"] = midwest_central_attrs["P_mm_day"] * 365
print(midwest_central_attrs["P_mm_yr"].describe())
print(
    "10th percentile of Precipitation", midwest_central_attrs["P_mm_yr"].quantile(0.1)
)
print(
    "90th percentile of Precipitation", midwest_central_attrs["P_mm_yr"].quantile(0.9)
)
# %%
print("--------------------------------")
print("Population density")
print(midwest_central_attrs["PDEN_2000_BLOCK"].describe())
print(
    "10th percentile of Population density",
    midwest_central_attrs["PDEN_2000_BLOCK"].quantile(0.1),
)
print(
    "90th percentile of Population density",
    midwest_central_attrs["PDEN_2000_BLOCK"].quantile(0.9),
)
# %% West and Southwest clusters
west_southwest_clusters = [2, 3, 4]
west_southwest_attrs = attrs[attrs["cluster"].isin(west_southwest_clusters)]
west_southwest_attrs.head()
# %%
print("--------------------------------")
print("Elevation")
print(west_southwest_attrs["ELEV_MEAN_M_BASIN"].describe())
print(
    "10th percentile of Elevation",
    west_southwest_attrs["ELEV_MEAN_M_BASIN"].quantile(0.1),
)
print(
    "90th percentile of Elevation",
    west_southwest_attrs["ELEV_MEAN_M_BASIN"].quantile(0.9),
)
# %%
print("--------------------------------")
print("Temperature")
print(west_southwest_attrs["T_AVG_BASIN"].describe())
print(
    "10th percentile of Temperature", west_southwest_attrs["T_AVG_BASIN"].quantile(0.1)
)
print(
    "90th percentile of Temperature", west_southwest_attrs["T_AVG_BASIN"].quantile(0.9)
)
# %%
print("--------------------------------")
print("Precipitation")
west_southwest_attrs["P_mm_yr"] = west_southwest_attrs["P_mm_day"] * 365
print(west_southwest_attrs["P_mm_yr"].describe())
print("10th percentile of Precipitation", west_southwest_attrs["P_mm_yr"].quantile(0.1))
print("90th percentile of Precipitation", west_southwest_attrs["P_mm_yr"].quantile(0.9))

# %%
