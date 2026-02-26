# %%
# Plot the data availability
# Ryoko Araki (@ry4git), 2026

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.collections import LineCollection
import matplotlib.dates as mdates

# %%
home_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
data_dir = r"D:\data"
qa_dir = os.path.join(home_dir, "out", "caravan_datacheck")
gages2_qa_file = os.path.join(qa_dir, "gages2_summary.csv")
hysets_qa_file = os.path.join(qa_dir, "hysets_summary.csv")
camels_qa_file = os.path.join(qa_dir, "camels_summary.csv")

# %% Load quality control file from both GAGES II and Caravan
qa_gages2 = pd.read_csv(gages2_qa_file)
qa_hysets = pd.read_csv(hysets_qa_file)
qa_camels = pd.read_csv(camels_qa_file)

# %% Drop overlapping gauges
qa_gages2["gauge_num"] = qa_gages2["gauge_id"].astype(str).str.zfill(8)

# %%
qa_gages2.head()
# %%
qa_hysets["gauge_num"] = (
    qa_hysets["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)

# %%
qa_hysets.head()
# %%
qa_camels["gauge_num"] = (
    qa_camels["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)
# %%
qa_camels.head()
# %%
print(len(qa_gages2), len(qa_hysets), len(qa_camels))
# %%
overlap_idx = qa_gages2["gauge_num"].isin(qa_hysets["gauge_num"]) | qa_gages2[
    "gauge_num"
].isin(qa_camels["gauge_num"])
print(len(overlap_idx))
# %%
# Prioritize Caravan (CAMELS and HYSETS) data over GAGES II data
qa_gages2 = qa_gages2[~overlap_idx]

qa_gages2.head()
# %% Get the data duration
qa_gages2["start_date"] = pd.to_datetime(qa_gages2["start_date"])
qa_gages2["end_date"] = pd.to_datetime(qa_gages2["end_date"])
qa_gages2["duration_yr"] = (
    qa_gages2["end_date"] - qa_gages2["start_date"]
).dt.days / 365

qa_hysets["start_date"] = pd.to_datetime(qa_hysets["start_date"])
qa_hysets["end_date"] = pd.to_datetime(qa_hysets["end_date"])
qa_hysets["duration_yr"] = (
    qa_hysets["end_date"] - qa_hysets["start_date"]
).dt.days / 365

qa_camels["start_date"] = pd.to_datetime(qa_camels["start_date"])
qa_camels["end_date"] = pd.to_datetime(qa_camels["end_date"])
qa_camels["duration_yr"] = (
    qa_camels["end_date"] - qa_camels["start_date"]
).dt.days / 365

# %% Drop data duration < 5 years
qa_gages2 = qa_gages2[qa_gages2["duration_yr"] > 5]
qa_hysets = qa_hysets[qa_hysets["duration_yr"] > 5]
qa_camels = qa_camels[qa_camels["duration_yr"] > 5]
print(
    f"GAGES II: {len(qa_gages2)} gauges, HYSETS: {len(qa_hysets)} gauges, CAMELS: {len(qa_camels)} gauges"
)
# %% Drop nan data > 30%
qa_gages2 = qa_gages2[qa_gages2["subset_nan_fraction"] < 0.3]
qa_hysets = qa_hysets[qa_hysets["subset_nan_fraction"] < 0.3]
qa_camels = qa_camels[qa_camels["subset_nan_fraction"] < 0.3]
print(
    f"GAGES II: {len(qa_gages2)} gauges, HYSETS: {len(qa_hysets)} gauges, CAMELS: {len(qa_camels)} gauges"
)
# %% Drop the area error > 25%
area_err_thresh = 0.25

# %% Load caravan attributes
attrs_dir = os.path.join(data_dir, "Caravan1.4", "attributes")
attrs_caravan_hys = pd.read_csv(
    os.path.join(attrs_dir, "hysets", "attributes_other_hysets.csv")
)
attrs_caravan_hys["gauge_num"] = (
    attrs_caravan_hys["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)

# %%
attrs_caravan_camels = pd.read_csv(
    os.path.join(attrs_dir, "camels", "attributes_other_camels.csv")
)
attrs_caravan_camels["gauge_num"] = (
    attrs_caravan_camels["gauge_id"].str.split("_").str[1].astype(str).str.zfill(8)
)
attrs_caravan = pd.concat([attrs_caravan_hys, attrs_caravan_camels])
print(len(attrs_caravan))

# %%
attrs_caravan.columns
# %% Load GAGES2 attributes
attrs_gages2_file = os.path.join(
    home_dir, "data", "GAGES2", "GAGES_II_attrs", "gagesII_sept30_2011_concat.csv"
)

attrs_gages2 = pd.read_csv(attrs_gages2_file)
attrs_gages2["gauge_num"] = attrs_gages2["usgs_gauge_id"].astype(str).str.zfill(8)
print(len(attrs_gages2))
# Make sure both columns are same
attrs_gages2.head()
# %%
attrs_both = attrs_caravan.merge(
    attrs_gages2, how="inner", left_on="gauge_num", right_on="gauge_num"
)
print(len(attrs_both))

# %%
attrs_both["area_err"] = abs(
    (attrs_both["area"] - attrs_both["DRAIN_SQKM"]) / attrs_both["DRAIN_SQKM"]
)
area_err_idx = attrs_both[attrs_both["area_err"] > area_err_thresh]["gauge_num"]

print(f"Area error threshold : (Caravan - GAGES2)/GAGES2 error > {area_err_thresh}")
print(
    f"{len(attrs_both[attrs_both['area_err'] < area_err_thresh])} survived after area error filtering ({len(attrs_both[attrs_both['area_err'] < area_err_thresh]) / len(attrs_both) * 100:.1f} %)"
)

# %% Drop the gauges with area error > 25%
qa_hysets_filt = qa_hysets[~qa_hysets["gauge_num"].isin(area_err_idx.values)]
qa_camels_filt = qa_camels[~qa_camels["gauge_num"].isin(area_err_idx.values)]

print(len(qa_hysets_filt), len(qa_camels_filt))

# %% Finally concat and plot the data availability
qa_gages2_filt = qa_gages2.copy()

qa_concat = pd.concat(
    [
        qa_gages2_filt,
        qa_hysets_filt.drop(columns=["gauge_id"]),
        qa_camels_filt.drop(columns=["gauge_id"]),
    ]
)
print(len(qa_concat))
qa_concat.head()

# %% Plot data availability (one bar per gauge, colored by subset_nan_fraction)
df = qa_concat.copy()

# Sort by start_date then subset_nan_fraction (stable ordering)
df = df.sort_values(["start_date", "subset_nan_fraction"]).reset_index(drop=True)

# Build line segments for LineCollection
x_start = mdates.date2num(pd.to_datetime(df["start_date"]))
x_end = mdates.date2num(pd.to_datetime(df["end_date"]))
y_positions = np.arange(len(df))
segments = [((xs, y), (xe, y)) for xs, xe, y in zip(x_start, x_end, y_positions)]

# Color map by subset_nan_fraction
cmap = plt.get_cmap("RdYlBu_r")
norm = plt.Normalize(
    vmin=float(df["subset_nan_fraction"].min()),
    vmax=float(df["subset_nan_fraction"].max()),
)
colors = cmap(norm(df["subset_nan_fraction"].to_numpy(dtype=float)))

height_inches = min(4, max(3, len(df) * 0.003))
fig, ax = plt.subplots(figsize=(8, height_inches))
lc = LineCollection(segments, colors=colors, linewidths=1, antialiased=True)
lc.set_rasterized(True)
ax.add_collection(lc)

# Axes formatting
ax.set_xlim(x_start.min(), x_end.max())
ax.set_ylim(-1, len(df))
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.autofmt_xdate()

ax.set_xlabel("Date")
ax.set_ylabel("Gauge")

# Optional: show sparse y tick labels if not too many gauges
if len(df) <= 50:
    ax.set_yticks(y_positions)
    # Prefer gauge_id if present, else gauge_num, else row index
    if "gauge_id" in df.columns:
        ax.set_yticklabels(df["gauge_id"])
    elif "gauge_num" in df.columns:
        ax.set_yticklabels(df["gauge_num"])
    else:
        ax.set_yticklabels(df.index.astype(str))
else:
    ax.set_yticks([])

# Colorbar
sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.01)
cbar.set_label("Fraction of missing data")

ax.set_title("Streamflow data availability")
plt.tight_layout()
plt.show()
plt.savefig(
    os.path.join(qa_dir, "fig_data_availability.png"), dpi=300, bbox_inches="tight"
)
# %%


# %% Make the same availability plots per dataset (GAGES II, HYSETS, CAMELS)
def _plot_availability(df_in: pd.DataFrame, title: str, outfile: str) -> None:
    df = df_in.copy()
    # Ensure required columns
    required_cols = {"start_date", "end_date", "subset_nan_fraction"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for plotting: {missing}")

    # Sort by start_date then subset_nan_fraction
    df = df.sort_values(["start_date", "subset_nan_fraction"]).reset_index(drop=True)

    # Build line segments
    x_start = mdates.date2num(pd.to_datetime(df["start_date"]))
    x_end = mdates.date2num(pd.to_datetime(df["end_date"]))
    y_positions = np.arange(len(df))
    segments = [((xs, y), (xe, y)) for xs, xe, y in zip(x_start, x_end, y_positions)]

    # Colors by NaN fraction
    cmap = plt.get_cmap("RdYlBu_r")
    norm = plt.Normalize(
        vmin=float(df["subset_nan_fraction"].min()),
        vmax=float(df["subset_nan_fraction"].max()),
    )
    colors = cmap(norm(df["subset_nan_fraction"].to_numpy(dtype=float)))

    height_inches = min(4, max(3, len(df) * 0.003))
    fig, ax = plt.subplots(figsize=(8, height_inches))
    lc = LineCollection(segments, colors=colors, linewidths=1, antialiased=True)
    lc.set_rasterized(True)
    ax.add_collection(lc)

    # Axes formatting
    ax.set_xlim(x_start.min(), x_end.max())
    ax.set_ylim(-1, len(df))
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()

    ax.set_xlabel("Date")
    ax.set_ylabel("Gauge")

    # Optional y tick labels
    if len(df) <= 50:
        ax.set_yticks(y_positions)
        if "gauge_id" in df.columns:
            ax.set_yticklabels(df["gauge_id"])
        elif "gauge_num" in df.columns:
            ax.set_yticklabels(df["gauge_num"])
        else:
            ax.set_yticklabels(df.index.astype(str))
    else:
        ax.set_yticks([])

    # Colorbar
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.01)
    cbar.set_label("Fraction of missing data")

    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(os.path.join(qa_dir, outfile), dpi=300, bbox_inches="tight")
    plt.show()


_plot_availability(
    qa_gages2_filt,
    "GAGES II streamflow availability",
    "fig_data_availability_gages2.png",
)
_plot_availability(
    qa_hysets_filt, "HYSETS streamflow availability", "fig_data_availability_hysets.png"
)
_plot_availability(
    qa_camels_filt, "CAMELS streamflow availability", "fig_data_availability_camels.png"
)


# %%
