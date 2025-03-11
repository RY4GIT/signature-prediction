# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# %%
# Load the SHAP values data from the CSV file
out_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf\output_flipl_20250311_test"
shap_values_df = pd.read_csv(os.path.join(out_dir, "shap_values.csv"))


# Split the feature.value column into feature and value
shap_values_df[["feature", "feature_value"]] = shap_values_df[
    "feature.value"
].str.split("=", expand=True)
shap_values_df["feature_value"] = shap_values_df["feature_value"].astype(float)

# %%
# Get the unique signatures
signatures = shap_values_df["sig_name"].unique()

for sig in signatures:
    plt.figure(figsize=(6, 4))
    sig_data = shap_values_df[shap_values_df["sig_name"] == sig]

    # Order the data by the largest absolute SHAP value
    sig_data = sig_data.reindex(
        sig_data["phi"].abs().sort_values(ascending=False).index
    )

    # Determine the color based on the SHAP value
    colors = ["tab:pink" if val < 0 else "skyblue" for val in sig_data["phi"]]

    # Create a horizontal bar plot
    plt.barh(
        sig_data["feature"],
        sig_data["phi"],
        xerr=sig_data["phi.var"],
        color=colors,
        edgecolor="lightgrey",
        alpha=0.7,
        ecolor="grey",  # Color of the error bars
        capsize=3,  # Add caps to the error bars
        error_kw={"alpha": 0.5},  # Increase transparency of the error bars
    )

    plt.xlabel("SHAP Value")
    plt.ylabel("Attribute")
    plt.title(f"{sig}")
    plt.gca().invert_yaxis()  # Invert y-axis to have the highest values on top
    plt.tight_layout()
    plt.xticks(rotation=20)
    plt.show()


# %%
