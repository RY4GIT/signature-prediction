# %%
import yaml
import os

# %%
#######################################################
# START CONFIG
# CHANGE HERE FOR YOUR PURPOSE
#######################################################

# OS type
os_type = "linux"  # "linux" or "win"

# List of clusters
clusters = [0, 1, 2, 3, 4, 5]

# %%
# File path
if os_type == "win":
    home_dir = "G:/Shared drives/Signatures -- large scale/baseflow"
    rf_out_dir = "RAraki/out/rf"
    sigs_file = "RAraki/out/signatures/caravan_us_20240609_tunedparams/out_calc_All_custom_filt.csv"
    attrs_file = "AHolt/data/derived_attrs/assembled_RA/attrs_caravan_us_hammondv2.csv"

    config_out_dir = (
        rf"C:\Users\flipl\dev\signature-prediction\random_forest\configs\{os_type}"
    )

elif os_type == "linux":
    home_dir = "/home/raraki/data/signature-prediction"
    rf_out_dir = "/out/rf"
    sigs_file = "/signatures/caravan_us_20250223_withWu/out_calc_All_custom_filt_qc_snow_area_gages2subset.csv"
    attrs_file = "/derived_attrs/assembled_RA/attrs_cara_and_gages2+climate+morph+padcat+cluster.csv"

    config_out_dir = (
        rf"C:\Users\flipl\dev\signature-prediction\random_forest\configs\{os_type}"
    )
if not os.path.exists(config_out_dir):
    os.makedirs(config_out_dir)
# %%
# ________________________________________________________________________________________________________
# Template YAML content

# ### Signatures to predict: we excluded signatures that are known to be unstable based on McMillan et al., 2021.
# The full list of signature candidates & thought processes are saved in:
# "G:\Shared drives\Signatures -- large scale\baseflow\RAraki\docs\sig_analysis.xlsx"
# https://docs.google.com/spreadsheets/d/1zYj7LPZeTagrsIV9iXbIKLM4lpyjUPbT?rtpof=true&usp=drive_fs

# ### Attributes to use: we excluded attributes that are
# - Not landscape attributes (attributes of Hydrology group, and soil erosion rate)
# - Categorical variables, following Annie’s analysis
# - Monthly climate variables (e.g., average PET in January, February, …), because hard to choose the representative values & they need to be (ideally) represented by annual statistics
# - Speaman’s corr  |$\rho$| > 0.8
# - Results: 26 attributes survived
# The full list of available Caravan attributes & thought processes are saved in:
# "G:\Shared drives\Signatures -- large scale\baseflow\RAraki\docs\attrs_analysis.xlsx"
# https://docs.google.com/spreadsheets/d/1eGk1OD4mCt3UmlyhUv27iXp5V0MfjZO0?rtpof=true&usp=drive_fs


template_yaml = {
    "paths": {
        "home_dir": home_dir,
        "out_dir": rf_out_dir,
        "train": {
            "signatures": sigs_file,
            "attributes": attrs_file,
        },
        "test": {"attributes": attrs_file},
    },
    "experiment_name": "cluster_template",
    "filter_by_cluster": {"run": True, "name": "cluster_template"},
    "settings": {"seed": 0, "ntree": 500, "num_folds": 10, "eval_metric": "RMSE"},
    "parallel": {"nCores": 16},
    "sigs_predict": [
        "TotalRR",
        "RR_Seasonality",
        "EventRR",
        "Recession_a_Seasonality",
        "AverageStorage",
        "RecessionParameters_b",
        "RecessionParameters_T0",
        "First_Recession_Slope",
        "Mid_Recession_Slope",
        "EventRR_TotalRR_ratio",
        "VariabilityIndex",
        "BFI",
        "BaseflowRecessionK",
        "IE_thresh_signif",
        "SE_thresh_signif",
        "Storage_thresh_signif",
        "IE_thresh",
        "SE_thresh",
        "IE_effect",
        "SE_effect",
        "Storage_thresh",
        "SE_slope",
        "R_Pvol_RC",
        "R_Pint_RC",
    ],
    "attrs_of_interest": [
        "ELEV_MEAN_M_BASIN",
        "DRAIN_SQKM",
        "SLOPE_PCT",
        "FORESTNLCD06",
        "CROPSNLCD06",
        "PASTURENLCD06",
        "PCT_IRRIG_AG",
        "SNOWICENLCD06",
        "PADCAT1_AND_2",
        "isowet_areafrac",
        "CLAYAVE",
        "SILTAVE",
        "OMAVE",
        "kar_pc_sse",
        "geol_weighted_ave_age_ma",
        "PDEN_2000_BLOCK",
        "gdp_ud_sav",
        "FRAGUN_BASIN",
        "P_mm_day",
        "PET_mm_day",
        "ARIDITY_GAGES2",
        "SNOW_PCT_PRECIP",
        "PRECIP_SEAS_IND",
        "high_prec_freq",
        "low_prec_freq",
        "low_prec_dur",
    ],
}
#######################################################
# END CONFIG ######
#######################################################

# %%
# ________________________________________________________________________________________________________
# Generate the YAML files

# ___________________________________________
# By cluster


# Function to generate YAML files
def generate_yaml_files(clusters, template_yaml, out_dir):
    for cluster_num in clusters:
        yaml_content = template_yaml.copy()

        yaml_content["experiment_name"] = f"cluster_{cluster_num}"
        yaml_content["filter_by_cluster"]["name"] = cluster_num

        # Define the output filename
        output_filename = f"config_cluster_{cluster_num}.yml"

        # Write the YAML content to the file
        with open(os.path.join(out_dir, output_filename), "w") as file:
            yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


generate_yaml_files(clusters, template_yaml, config_out_dir)
# %%

# ______________________
# Whole CONUS
yaml_content = template_yaml.copy()

# Modify the experiment_name and filter_by_cluster$name
yaml_content["experiment_name"] = f"cluster_all"
yaml_content["filter_by_cluster"]["run"] = False
yaml_content["filter_by_cluster"]["name"] = "NA"

# Define the output filename
output_filename = f"config_cluster_all.yml"

# Write the YAML content to the file
with open(os.path.join(config_out_dir, output_filename), "w") as file:
    yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


print(f"Output results to {config_out_dir}")

# %%
