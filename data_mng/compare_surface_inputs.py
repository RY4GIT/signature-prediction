# %%
import pandas as pd
import os

# %%
gauge_id = "01443500"


surface_input_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\surface_water_input_Hammond\preprocessed"
caravan_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\Caravan1.4\timeseries\csv"
hysets_dir = os.path.join(caravan_dir, "hysets")
camels_dir = os.path.join(caravan_dir, "camels")

# %%
surface_input = pd.read_csv(
    os.path.join(surface_input_dir, f"gages2_{gauge_id}.csv"), index_col="date"
)
surface_input
# %%
camels_filname = os.path.join(camels_dir, f"camels_{gauge_id}.csv")
hysets_filename = os.path.join(hysets_dir, f"hysets_{gauge_id}.csv")
if os.path.exists(camels_filname):
    print("data exists in camels")
    caravan_input = pd.read_csv(camels_filname, index_col="date")
elif os.path.exists(hysets_filename):
    print("data exists in hysets")
    caravan_input = pd.read_csv(hysets_filename, index_col="date")
else:
    print("data doesn't exist")
# %%
df = surface_input.join(caravan_input, how="left")

df.columns

# %%
df["total_surface_input_mm"] = df["melt_mm"] + df["mix_mm"] + df["rain_mm"]
# %%
import matplotlib.pyplot as plt

# Set a larger figure size
fig, ax = plt.subplots(figsize=(20, 4))

# Define custom colors for each variable
custom_colors = {
    "melt_mm": "#d7b5d8",
    #   "mix_mm": "#756bb1",
    #  "rain_mm": "#3182bd",
    "total_surface_input_mm": "#3182bd",
    "total_precipitation_sum": "#fb6a4a",
}

start_year = 2002
start_date = f"{start_year}-10-01"
end_date = f"{start_year + 1}-09-30"
# Plot each column separately with custom colors
for col, color in custom_colors.items():
    df.loc[start_date:end_date][col].plot(
        ax=ax,
        marker="o",
        linestyle="-",
        alpha=0.7,
        color=color,
        label=col,
        markersize=2,
    )

# Add title and labels
ax.set_title("Precipitation Components Over Time", fontsize=14)
ax.set_xlabel("Time", fontsize=12)
ax.set_ylabel("Precipitation (mm)", fontsize=12)

# Improve legend placement
ax.legend(title="Precipitation Type", loc="upper left", fontsize=10)

# Add grid for readability
ax.grid(True, linestyle="--", alpha=0.5)
plt.xticks(rotation=45)
# Show plot
plt.show()


# %%
