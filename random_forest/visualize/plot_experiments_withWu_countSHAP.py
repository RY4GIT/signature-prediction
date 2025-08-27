# %%
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# %% #########################################################
# Configs
#############################################################

########################## CHANGE HERE #################
cloud_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki"
rf_dir = os.path.join(cloud_dir, "out", "rf")
rf_out_dir = os.path.join(
    rf_dir, "output_raraki_20250826_cluster_all"
)  # Random forest output directory (except Wu's)
fig_dir = os.path.join(
    rf_dir, "output_raraki_20250826_figures"
)  # Figure output directory
rf_out_dir_Wu = os.path.join(
    rf_dir, "output_raraki_20250827_cluster_all_Wu"
)  # Wu's random forest output directory
user_name = "raraki"  # User name
# file_type = "png"  # or "pdf" if you prefer PDF output
file_type = "pdf"
########################################################

if not os.path.exists(fig_dir):
    os.makedirs(fig_dir)

# %% #########################################################
# Plot configs
#############################################################

# Current directory
os.chdir(r"C:\Users\flipl\dev\signature-prediction\random_forest\visualize")

# Attributes info & colors
config_attrs_info_file = "plot_config_attrs_info.csv"
attrs_info = pd.read_csv(config_attrs_info_file)
with open("plot_config_attrs_colors.json", "r") as file:
    attrs_colors = json.load(file)

# Cluster colors
with open("plot_config_expcolors_clusters.json", "r") as file:
    cluster_plot_json = json.load(file)
# Convert keys to integers except for the first item
cluster_info = {int(k) if k.isdigit() else k: v for k, v in cluster_plot_json.items()}
clusters = cluster_info.keys()
print(clusters)


# Function to map colors
def map_colors(group):
    return attrs_colors.get(group, "lightgrey")


# Function to create color dictionary
def create_color_dict(df, var_name):
    df["color"] = df["Group"].apply(map_colors)
    return df.set_index(var_name)["color"].to_dict()


# %% #########################################################
# Signature info
#############################################################

# Signature info
sigs_RF_names_ordered = [
    "BFI",
    "BaseflowRecessionK",
    "AverageStorage",
    "RecessionParameters_b",
    "TotalRR",
    "EventRR",
    "Recession_a_Seasonality",
    "VariabilityIndex",
    "IE_thresh",
    "IE_thresh_signif",
    "SE_thresh",
    "SE_thresh_signif",
    "R_Pint_RC",
    "R_Pvol_RC",
]
sig_Wu_names = [
    "R_Pint_RC",
    "R_Pvol_RC",
]


# %% #########################################################
# Load Caravan attributes
#############################################################

attrs_path = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\data\derived_attrs\assembled_RA\attrs_cara_gages2_etc_20250517+cluster.csv"
attrs = pd.read_csv(attrs_path)
attrs["gauge_id"] = attrs["gauge_id"].astype(str)

attrs.head()

# %% #########################################################
# Load SHAP data
#############################################################

# Load Wu's SHAP data
_df_shap_Wu = pd.read_csv(os.path.join(rf_out_dir_Wu, "shap_values.csv"))
# Load other SHAP data
_df_shap = pd.read_csv(os.path.join(rf_out_dir, "shap_values.csv"))
# Remove Wu's signatures
_df_shap = _df_shap[~_df_shap["sig_name"].isin(sig_Wu_names)]
df_shap = pd.concat([_df_shap, _df_shap_Wu], axis=0)

# Make sure the data is float
df_shap["feature_value"] = df_shap["feature_value"].astype(float)
df_shap["phi"] = df_shap["phi"].astype(float)
df_shap["phi.var"] = df_shap["phi.var"].astype(float)
df_shap = df_shap.merge(
    attrs_info, how="left", left_on="feature", right_on="variable_name"
)
print(len(df_shap))
df_shap.tail()


# %%
# Join df_SHAP with attrs_camels and attrs_hysets on gauge_id
print("Joining SHAP data with attrs_camels and attrs_hysets...")
df_shap_with_attrs = df_shap.merge(attrs, how="left", on="gauge_id")
print(len(df_shap_with_attrs))

# %% #########################################################
# Adjust the cluster column
#############################################################

# Map original cluster labels to broader regions
cluster_to_reclass = {
    1: "Eastern U.S.",
    5: "Eastern U.S.",
    2: "West",
    3: "West",
    4: "West",
    0: "Midwest",
}
df_shap_with_attrs = df_shap_with_attrs.dropna(subset=["cluster"])
grouping_col = "region"
cluster_num = pd.to_numeric(df_shap_with_attrs["cluster"], errors="coerce").astype(
    "Int64"
)
df_shap_with_attrs[grouping_col] = cluster_num.map(cluster_to_reclass)

# %% #########################################################
# COUNT SHAP VALUES PER GAUGE
#############################################################

########################CHANGE HERE#####################

# Assign 1 score if the absolute SHAP value is top {top_n} for a given gauge and signature

top_n = 3  # Number of top attributes to assign 1 score
regions = ["Eastern U.S.", "Midwest", "West", "all"]  # Regions to show
show_k = 10  # Number of attributes to show in plots

#############################################################

# Rank absolute SHAP within each gauge and signature, then flag top-N
print("Ranking absolute SHAP values...")

# Get the absolute SHAP value
df_shap_with_attrs["phi_abs"] = df_shap_with_attrs["phi"].abs()

# Rank absolute SHAP within each gauge and signature
df_shap_with_attrs["rank_abs_phi"] = df_shap_with_attrs.groupby(
    ["gauge_id", "sig_name"]
)["phi_abs"].rank(method="first", ascending=False)

# Flag top-N
df_shap_with_attrs["is_top_n"] = (df_shap_with_attrs["rank_abs_phi"] <= top_n).astype(
    int
)

# %% #########################################################
# Count the score per cluster
#############################################################

# Aggregate counts of top-N occurrences per cluster per signature and attribute
print(f"Counting top-{top_n} SHAP values per cluster...")
df_top_counts = (
    df_shap_with_attrs[df_shap_with_attrs["is_top_n"] == 1]
    .groupby([grouping_col, "sig_name", "feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)

# Compute an overall (all regions) summary
df_top_counts_all = (
    df_shap_with_attrs[df_shap_with_attrs["is_top_n"] == 1]
    .groupby(["sig_name", "feature", "Group"], dropna=False)
    .agg(count=("is_top_n", "sum"))
    .reset_index()
)
df_top_counts_all[grouping_col] = "all"

# Concatenate the overall summary with the per-region summaries
df_top_counts = pd.concat([df_top_counts, df_top_counts_all], ignore_index=True)

# %% #########################################################
# Show and save the table for the top 10 SHAP values per region
#############################################################


print(f"Showing and saving the table for the top {show_k} SHAP values per region...")
for region in regions:
    for sig in sigs_RF_names_ordered:
        # Subset the data
        dfc = df_top_counts[
            (df_top_counts[grouping_col] == region) & (df_top_counts["sig_name"] == sig)
        ].sort_values("count", ascending=False)
        top_attrs = dfc.head(show_k)
        print(f"{region} — top {top_n} attributes by SHAP-count:")
        if top_attrs.empty:
            print("  (no data)")
        else:
            print(top_attrs[["feature", "Group", "count"]].to_string(index=False))
        print("--------------------------------")

# Out put them as csv file
df_top_counts.to_csv(
    os.path.join(fig_dir, f"top{top_n}_attrs_by_SHAP_count.csv"), index=False
)


# %% #########################################################
# SHOW THE COUNTS IN BAR PLOTS  — ONE SUBPLOT PER SIGNATURE
#############################################################


def plot_tile_counts_grid_by_region_all_sigs(
    df_counts: pd.DataFrame,
    sig_list: list,
    region: str,
    top_k_features: int = 15,
    top_n: int = 3,
):
    # Create a figure with subplots
    n_cols = 5
    n_rows = (len(sig_list) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(4 * n_cols, 2.8 * n_rows),
        constrained_layout=True,
    )
    axes = axes.flatten()

    # Plot each signature
    for i, sig_name in enumerate(sig_list):
        ax = axes[i]

        # Subset the data
        df_sig = df_counts[
            (df_counts["sig_name"] == sig_name) & (df_counts[grouping_col] == region)
        ].copy()
        if df_sig.empty:
            ax.set_visible(False)
            continue

        # Map colors from Group
        if "color" not in df_sig.columns:
            df_sig["color"] = df_sig["Group"].map(attrs_colors)

        # Aggregate total counts per feature and group, keep color/group for each feature
        df_totals = (
            df_sig.groupby(["feature", "Group", "color"], dropna=False)["count"]
            .sum()
            .reset_index()
            .sort_values("count", ascending=False)
            .groupby("feature")
            .first()
            .sort_values("count", ascending=False)
        )
        features_to_show = list(df_totals.index[:top_k_features])

        # Build plotting frame
        # Select the top features
        df_plot = (
            df_totals.loc[features_to_show]
            .reset_index()
            .rename(columns={"count": "total_count"})
        )

        # Show the top features
        df_plot["feature"] = pd.Categorical(
            df_plot["feature"], categories=features_to_show, ordered=True
        )
        ax.barh(
            y=df_plot["feature"],
            width=df_plot["total_count"],
            color=df_plot["color"],
            edgecolor="dimgray",
        )
        ax.invert_yaxis()
        ax.set_title(sig_name, fontsize=10, loc="left")
        ax.set_xlabel("Top-N count")
        ax.set_ylabel(None)
        ax.tick_params(labelsize=7)

    # Hide any extra axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(f"Top {top_n} SHAP count — {region}", fontsize=14)
    out_grid = f"bar_SHAPcount_by_region_all_signatures_{region}_top{top_n}.{file_type}"
    fig.savefig(os.path.join(fig_dir, out_grid), dpi=300, bbox_inches="tight")
    # plt.close(fig)


for region in regions:
    print(f"Plotting the top {top_n} SHAP count for {region}...")
    plot_tile_counts_grid_by_region_all_sigs(
        df_top_counts,
        sigs_RF_names_ordered,
        region=region,
        top_k_features=12,
        top_n=top_n,
    )

# %%
