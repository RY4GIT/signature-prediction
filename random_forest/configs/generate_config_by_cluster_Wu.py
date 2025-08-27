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

config_out_dir = (
    rf"C:\Users\flipl\dev\signature-prediction\random_forest\configs\{os_type}"
)
if not os.path.exists(config_out_dir):
    os.makedirs(config_out_dir)

# %%
# File path that goes into the config
if os_type == "win":
    home_dir = "G:/Shared drives/Signatures -- large scale/baseflow"
    rf_out_dir = "RAraki/out/rf"
    sigs_file = (
        "RAraki/out/signatures/Wu_sigs_20250812/out_sigEvent_cara_gg2_rf_train.csv"
    )
    attrs_file = "AHolt/data/derived_attrs/assembled_RA/attrs_cara_gages2_etc_20250517+cluster.csv"

elif os_type == "linux":
    home_dir = "/home/raraki/data/signature-prediction"
    rf_out_dir = "/out/rf"
    sigs_file = "/signatures/Wu_sigs_20250812/out_sigEvent_cara_gg2_rf_train.csv"
    attrs_file = (
        "/derived_attrs/assembled_RA/attrs_cara_gages2_etc_20250517+cluster.csv"
    )


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
    "save_models": True,
    "parallel": {"nCores": 16},
    "sigs_predict": [
        "R_Pvol_RC",
        "R_Pint_RC",
    ],
    "attrs_of_interest": [
        "ELEV_MEAN_M_BASIN",
        "DRAIN_SQKM",
        "SLOPE_DEG_x10",
        "FORESTNLCD06",
        "CROPSNLCD06",
        "PASTURENLCD06",
        "PCT_IRRIG_AG",
        # "SNOWICENLCD06", # Drop uninformative variables
        "PADCAT1_AND_2",
        "isowet_areafrac",
        "CLAYAVE",
        "SILTAVE",
        "soc_th_sav",
        "kar_pc_sse",
        "geol_weighted_ave_age_ma",
        "PDEN_2000_BLOCK",
        # "gdp_ud_sav", # Drop uninformative variables
        # "hdi_ix_sav", # Drop uninformative variables
        "P_mm_day",
        "PET_mm_day",
        "ARIDITY_GAGES2",
        "SNOW_FRAC_PRECIP",
        "seasonality_FAO_PM",
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
        # yaml_content["save_models"] = False # Save all models

        # Define the output filename
        output_filename = f"config_cluster_{cluster_num}_Wu.yml"

        # Write the YAML content to the file
        with open(os.path.join(out_dir, output_filename), "w") as file:
            yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


generate_yaml_files(clusters, template_yaml, config_out_dir)
# %%

# ______________________
# Whole CONUS
yaml_content = template_yaml.copy()

# Modify the experiment_name and filter_by_cluster$name
yaml_content["experiment_name"] = "cluster_all"
yaml_content["filter_by_cluster"]["run"] = False
yaml_content["filter_by_cluster"]["name"] = "NA"

# Define the output filename
output_filename = "config_cluster_all_Wu.yml"

# Write the YAML content to the file
with open(os.path.join(config_out_dir, output_filename), "w") as file:
    yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


print(f"Output results to {config_out_dir}")

# %%
