# %%
import yaml
import os

# %%
#######################################################
# START CONFIG
# CHANGE HERE FOR YOUR PURPOSE
#######################################################

# OS type
os_type = "win"  # "linux" or "win"

# List of ecoregions
ecoregions = [
    "11  MEDITERRANEAN CALIFORNIA",
    "1210 Western Deserts",
    "6713 Western Mountains",
    "81 North Eastern Forests",
    "82 South Eastern Forests",
    "91 North Great Plains",
    "92 South Great Plains",
]

# Original EPA Level 1 ecoregion definition
# ecoregions = [
#     "5  NORTHERN FORESTS",
#     "10  NORTH AMERICAN DESERTS",
#     "11  MEDITERRANEAN CALIFORNIA",
#     "12  SOUTHERN SEMIARID HIGHLANDS",
#     "13  TEMPERATE SIERRAS",
#     "6  NORTHWESTERN FORESTED MOUNTAINS",
#     "7  MARINE WEST COAST FOREST",
#     "8  EASTERN TEMPERATE FORESTS",
#     "9  GREAT PLAINS",
# ]

# Hammond et al., 2021 definition
# ecoregions = [
#     "8  EASTERN TEMPERATE FORESTS"
#     "5  NORTHERN FORESTS"
#     "91 North Great Plains"
#     "92 South Great Plains"
#     "613 Western Mountains"
#     "1210 Western Deserts"
#     "11  MEDITERRANEAN CALIFORNIA"
#     "7  MARINE WEST COAST FOREST"
# ]

# Hammond et al., 2021 definition + further aggregating/splitting some regions
# ecoregions = [
#     "81 North Eastern Forests"
#     "82 South Eastern Forests"
#     "91 North Great Plains"
#     "92 South Great Plains"
#     "6713 Western Mountains"
#     "1210 Western Deserts"
#     "11  MEDITERRANEAN CALIFORNIA"
# ]
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
    sigs_file = (
        "/signatures/caravan_us_20240609_tunedparams/out_calc_All_custom_filt.csv"
    )
    attrs_file = "/derived_attrs/assembled_RA/attrs_caravan_us_hammondv2.csv"

    config_out_dir = (
        rf"/home/raraki/signature-prediction/random_forest/configs/{os_type}"
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

# Not sure why but "min_Qf_perc" doesn't work with Linux ...
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
    "experiment_name": "ecoregion_template",
    "filter_by_ecoregion": {"run": True, "name": "ecoregion_template"},
    "settings": {"seed": 0, "ntree": 500, "num_folds": 10, "eval_metric": "MSE"},
    "parallel": {"nCores": 16},
    "sigs_predict": [
        "TotalRR",
        "RR_Seasonality",
        "EventRR",
        "Recession_a_Seasonality",
        "AverageStorage",
        "RecessionParameters_1",
        "RecessionParameters_2",
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
    ],
    "attrs_of_interest": [
        "ele_mt_sav",
        "area",
        "sgr_dk_sav",
        "for_pc_sse",
        "crp_pc_sse",
        "pst_pc_sse",
        "ire_pc_sse",
        "prm_pc_sse",
        "pac_pc_sse",
        "isowet_areafrac",
        "cly_pc_sav",
        "slt_pc_sav",
        "soc_th_sav",
        "kar_pc_sse",
        "geol_weighted_ave_age_ma",
        "ppd_pk_sav",
        "gdp_ud_sav",
        "hdi_ix_sav",
        "p_mean",
        "pet_mean",
        "aridity",
        "frac_snow",
        "seasonality",
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
# By ecoregion


# Function to generate YAML files
def generate_yaml_files(ecoregions, template_yaml, out_dir):
    for ecoregion in ecoregions:
        # Create a copy of the template
        yaml_content = template_yaml.copy()

        # Modify the experiment_name and filter_by_ecoregion$name
        ecoregion_cleaned = ecoregion.replace("  ", "_").replace(
            " ", "_"
        )  # Clean up for filename
        ecoregion_num = ecoregion_cleaned.split("_")[0]
        yaml_content["experiment_name"] = f"ecoregion_{ecoregion_num}"
        yaml_content["filter_by_ecoregion"]["name"] = ecoregion

        # Define the output filename
        output_filename = f"config_ecoregion_{ecoregion_num}.yml"

        # Write the YAML content to the file
        with open(os.path.join(out_dir, output_filename), "w") as file:
            yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


generate_yaml_files(ecoregions, template_yaml, config_out_dir)
# %%

# ______________________
# Whole CONUS
yaml_content = template_yaml.copy()

# Modify the experiment_name and filter_by_ecoregion$name
yaml_content["experiment_name"] = f"caravan_us"
yaml_content["filter_by_ecoregion"]["run"] = False
yaml_content["filter_by_ecoregion"]["name"] = "NA"

# Define the output filename
output_filename = f"config_caravan_us.yml"

# Write the YAML content to the file
with open(os.path.join(config_out_dir, output_filename), "w") as file:
    yaml.dump(yaml_content, file, default_flow_style=False, sort_keys=False)


print(f"Output results to {config_out_dir}")

# %%
