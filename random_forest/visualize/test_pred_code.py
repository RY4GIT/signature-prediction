import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os

# Set plot style
plt.style.use("ggplot")
sns.set_theme(style="whitegrid")


def load_prediction_data(file_path):
    """Load prediction data from CSV file."""
    df = pd.read_csv(file_path)
    # Get model version from filename
    model_version = extract_model_version(file_path)
    df["model_version"] = model_version
    print(f"Loaded {file_path} with model version: {model_version}, shape: {df.shape}")
    return df


def extract_model_version(file_path):
    """Extract model version from filename."""
    file_name = Path(file_path).stem
    # Handle different naming patterns
    if "predicted_signatures_" in file_name:
        return file_name.replace("predicted_signatures_", "")
    else:
        # If the file doesn't follow the expected naming convention,
        # just return the filename as the model version
        return file_name


def create_direct_comparison_plots(df1, df2, output_dir):
    """Create scatter plots comparing predictions between two dataframes."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract model versions
    version1 = df1["model_version"].iloc[0]
    version2 = df2["model_version"].iloc[0]

    print(f"Comparing models: {version1} vs {version2}")

    # Get all unique signatures
    signatures = set(df1["sig_name"].unique()) & set(df2["sig_name"].unique())
    print(f"Found {len(signatures)} common signatures")

    for sig in signatures:
        # Filter data for the current signature
        sig_data1 = df1[df1["sig_name"] == sig]
        sig_data2 = df2[df2["sig_name"] == sig]

        # Merge on gauge_id
        merged_data = pd.merge(sig_data1[["gauge_id", "prediction", "model_version"]], sig_data2[["gauge_id", "prediction", "model_version"]], on="gauge_id", suffixes=("_1", "_2"))

        print(f"Signature {sig}: Found {len(merged_data)} common gauges")

        if len(merged_data) == 0:
            print(f"  Warning: No common gauges found for signature {sig}")
            continue

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Scatter plot
        ax.scatter(merged_data["prediction_1"], merged_data["prediction_2"], alpha=0.6)

        # Add diagonal line
        all_values = np.concatenate([merged_data["prediction_1"], merged_data["prediction_2"]])
        min_val = np.min(all_values)
        max_val = np.max(all_values)
        ax.plot([min_val, max_val], [min_val, max_val], "r--")

        # Calculate correlation
        corr = np.corrcoef(merged_data["prediction_1"], merged_data["prediction_2"])[0, 1]

        # Calculate RMSE
        rmse = np.sqrt(((merged_data["prediction_1"] - merged_data["prediction_2"]) ** 2).mean())

        # Add titles and labels
        ax.set_title(f"Comparison of {sig} predictions\nCorrelation: {corr:.4f}, RMSE: {rmse:.4f}")
        ax.set_xlabel(f"Model: {version1}")
        ax.set_ylabel(f"Model: {version2}")

        # Add text showing number of points
        ax.text(0.05, 0.95, f"N = {len(merged_data)}", transform=ax.transAxes, ha="left", va="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

        # Equal aspect ratio
        ax.set_aspect("equal", adjustable="box")

        # Save the plot
        plt.tight_layout()
        filename = f"{sig}_{version1}_vs_{version2}.png"
        plt.savefig(os.path.join(output_dir, filename), dpi=300)
        plt.close()  # Close the figure to save memory


def main():
    # Define paths to your prediction files
    train_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf\output_flipl_20250513_test\predicted_signatures_prediction.csv"
    prediction_file = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf\output_flipl_20250513_test\predicted_signatures_prediction_mp.csv"

    # Check if files exist
    if not os.path.exists(train_file):
        print(f"Error: File not found: {train_file}")
        return

    if not os.path.exists(prediction_file):
        print(f"Error: File not found: {prediction_file}")
        return

    # Load prediction dataframes
    df_train = load_prediction_data(train_file)
    df_prediction = load_prediction_data(prediction_file)

    # Create output directory
    output_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\RAraki\out\rf\output_flipl_20250513_test\comparison_plots"

    # Create comparison plots
    create_direct_comparison_plots(df_train, df_prediction, output_dir)

    print(f"Plots have been saved to {output_dir}")


if __name__ == "__main__":
    main()
