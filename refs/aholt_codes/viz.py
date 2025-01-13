from signatures.archive.calculate_sigs_camels import *
import geopandas
import matplotlib.pyplot as plt

# Author: Anne Holt (@annieholt)
# Date: 2024

# import data
pi_path = 'C:/Users/holta/Documents/Repositories/baseflow_prediction/signatures/camels_gw_sigs_pi.obj'
tossh_path = 'C:/Users/holta/Documents/Repositories/TOSSH'
sig_df = get_sig_df(tossh_path, pi_path)

# plot BFI
# need to make into geodataframe, using lat long

bfi_df = sig_df[["gauge_id", "gauge_lat", "gauge_lon", "TotalRR"]]
bfi_gdf = geopandas.GeoDataFrame(bfi_df, geometry=geopandas.points_from_xy(bfi_df.gauge_lon, bfi_df.gauge_lat))
print(bfi_gdf.head())

# now create dataset of 48 contiguous United States
# import from local file
usa = geopandas.read_file('D:/SDSU_GEOG/Thesis/Data/US states/cb_2018_us_state_500k/cb_2018_us_state_500k.shp')
state_names = ["Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut",
               "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Iowa", "Idaho",
               "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine",
               "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota",
               "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
               "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
               "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin",
               "West Virginia", "Wyoming"]
# only retain the 48 states
usa_48 = usa[usa['NAME'].isin(state_names)]

# create plot of gauges over state boundaries
# color by BFI
ax = usa_48.plot(color='white', edgecolor='black')
f = figsize=(9, 9)
bfi_gdf.plot(ax=ax, column="TotalRR", cmap="coolwarm_r", legend=True, legend_kwds={'shrink': 0.4})
plt.show()