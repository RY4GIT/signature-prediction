# %%
import pandas as pd
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %%
derived_attrs_dir = (
    r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data\derived_attrs"
)
caravan_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\attributes"
camels_attrs_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\CAMELS\camels-20240616T2045Z"
ecoregion_name = "hammondv2"
fig_out_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\AGU24"
if not os.path.exists(fig_out_path):
    os.makedirs(fig_out_path)

# %%

combined_cam_hys = pd.read_csv(
    os.path.join(
        derived_attrs_dir, "assembled_RA", f"attrs_caravan_us_{ecoregion_name}.csv"
    )
)
combined_cam_hys
# %% Plot

attribute_info = {
    "isowet_areafrac": {
        "label": "Isolated wetland area fraction",
        "unit": "(-)",
        "colormap": "YlGnBu",
        "vmin": 0.0,
        "vmax": 0.10,
    },
    "geol_weighted_ave_age_ma": {
        "label": "Average geologic age",
        "unit": "(Ma)",
        "colormap": "YlOrRd",
        "vmin": 500,
        "vmax": 3000,
    },
}


def plot_attr_map(df, attr_name, outlabel):

    # Set up the map
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), facecolor="white")

    land = cfeature.NaturalEarthFeature(
        "physical",
        "land",
        "50m",
        edgecolor="face",
        facecolor="lightgray",  # Set land color to light gray
    )
    ax.add_feature(land)

    # Add state lines with white color
    states = cfeature.NaturalEarthFeature(
        category="cultural",
        scale="50m",
        facecolor="none",
        name="admin_1_states_provinces_lines",
        edgecolor="white",
    )
    ax.add_feature(states, linewidth=0.5)  # , linestyle=":", alpha=0.5)

    # Set extent to CONUS
    ax.set_extent([-124.85, -66.95, 24.396308, 49.384358])

    # Add map features
    ax.add_feature(cfeature.COASTLINE, color="white")  # Set coastline color to grey
    ax.add_feature(cfeature.BORDERS, linewidth=1.0, linestyle=":", color="white")
    # ax.add_feature(cfeature.STATES, linestyle=":", color="white")

    # Plotting the filtered data
    scatter = ax.scatter(
        df["gauge_lon"],
        df["gauge_lat"],
        c=df[attr_name],
        cmap=attribute_info[attr_name]["colormap"],
        marker="o",
        # edgecolors="grey",
        s=5,
        alpha=0.8,
        zorder=99,
        vmin=attribute_info[attr_name]["vmin"],
        vmax=attribute_info[attr_name]["vmax"],
    )

    # Add a legend
    ax.set_title(
        f"{attribute_info[attr_name]["label"]} {attribute_info[attr_name]["unit"]}"
    )

    # Adding a colorbar
    plt.colorbar(scatter, ax=ax, shrink=0.4)

    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(fig_out_path, f"{attr_name}_{outlabel}.pdf"))


for attr_name in attribute_info:
    plot_attr_map(combined_cam_hys, attr_name, outlabel="cam_hys")

# %%
