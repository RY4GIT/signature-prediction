# signature-prediction
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![CodeStyle](https://img.shields.io/badge/code%20style-Ruff%20and%20Black-black)]()

This repository contains code for predicting hydrologic processes using signatures as detailed in the corresponding manuscript:

> Araki, R., Holt, A., Hammond, J. C., Husic, A., Coxon, G., and McMillan, H. K. (2026). Continental-scale prediction of hydrologic signatures and processes, Hydrology and Earth System Sciences (In Press)

The repository contains scripts to (a) calculate hydrologic signatures using TOSSH Toolbox functions, (b) to predict hydrologic signatures with random forest models, and (c) derive inferences from signatures and RF models.

It extends the work by [Holt & McMillan (2025)](https://doi.org/10.1002/hyp.70080). This repository was originally a fork of the repository created by Anne Holt: https://github.com/annieholt/Baseflow_Signature_Prediction

## Directory layout
### GitHub layout
    ├── data_mng                # Data management
    ├── figures                 # Visualization code for manuscripts and conference posters
    ├── random_forest           # Scripts to run the random forest models
    └── signatures              # Scripts to calculate hydrologic signatures using the TOSSH toolbox


## Getting started
If you have downloaded the finalized dataset (signature values, landscape attributes), you can skip to Step 5: Derive process inference.

### 1. Preparation
- Fork and clone the following repositories:
    ```
    git clone https:\\github.com\RY4GIT\signature-prediction.git
    ```
    ```
    git clone https:\\github.com\RY4GIT\TOSSH
    ```
    ```
    git clone https:\\github.com\RY4GIT\Wetland_GeologicAge_Attributes.git
    ```
- Download the Caravan v1.4 and v1.5 datasets
    - <https://zenodo.org/records/10968468>
- Download the GAGES2 datasets
    - Landscape attributes and GIS layer: <https://www.sciencebase.gov/catalog/item/631405bbd34e36012efa304a>
    - Streamflow data: <https://doi-usgs.github.io/dataRetrieval/>
    - gridMET forcing: <https://www.sciencebase.gov/catalog/item/6414b3f9d34eb496d1ceb5ae>
        - Use `data_mng\hydroclimatic_timeseries\curate_gages2.py` to combine gridMET and streamflow data
- Set up environments
    - Python environment: `environment_minimal.yml` or `environment.yml` (configured for Windows)
    - R environment: `random_forest\envs`
    - MATLAB: tested on versions 2020b–2024b

### 2. Calculate signatures and landscape attributes 
#### 2.1. Calculate hydrologic signatures (MATLAB)
- Calculate signatures using:  
    - ```signatures\main_caravan.m``` for calculating all basic TOSSH signatures for the Caravan dataset
    - ```signatures\WuSigs_main_caravan.m``` for calculating Wu et al., 2021 signatures for the Caravan dataset
    - ```signatures\main_gages2_gridmet.m``` for calculating all basic TOSSH signatures for the GAGES2 dataset
    - ```signatures\WuSigs_main_gages2.m``` for calculating Wu et al., 2021 signatures for the GAGES2 dataset
    - (experimental) ```signatures\main_gages2_swi.m``` for the GAGES2 dataset with the surface input dataset from [Hammond, 2024](https://www.sciencebase.gov/catalog/item/6494515fd34ef77fcb014eb0)

#### 2.2. Calculate additional landscape attributes (Python)
- Calculate additional attributes—wetland fraction and geologic ages (Holt and McMillan, 2025)—by following steps 1–3 in the [```Wetland_GeologicAge_Attributes```](https://github.com/RY4GIT/Wetland_GeologicAge_Attributes) repository


### 3. Prepare input and evaluation datasets for the random forest model
#### 3.1. Curate signature files (Python)
- Get data quality flags using ```data_mng\hydroclimatic_timeseries\qa_hysets.py``` and ```data_mng\hydroclimatic_timeseries\qa_gages2.py```
- Filter out some gauges and signatures using scripts in ```signatures\postprocess\```
    - `signatures\postprocess\postprocess_caravan_sigs_for_RF.py` for the Caravan dataset
    - `signatures\postprocess\postprocess_gages2_gridMET_sigs.py` for the GAGES2 dataset
    - `signatures\postprocess\postprocess_Wu2021.py` for Wu et al., 2021 signatures 
    - These scripts copy signature files with extension `_filt_qc.csv` (for meeting conditions 1 & 2), `_filt_qc_snow.csv` (for meeting conditions 1 & 2 & 3), and `_filt_qc_snow_area.csv` (for meeting conditions 1 & 2 & 3 & 4)
        1. Exclude Hysets watersheds with bad data quality (less than 5 years of record OR >30\% of the record is NaN for the period where data are available)
        2. Exclude Hysets watersheds overlapping with CAMELS OR Exclude GAGES2 watersheds overlapping with Caravan
        3. For event-based overland flow signatures, exclude Caravan and GAGES2 watersheds dominated by snow with `frac_snow` >20\%
        4. Exclude Caravan watersheds that have >25% error in estimated watershed drainage area between Caravan and GAGES-II estimates (31 watersheds)
#### 3.2. Assemble and curate landscape attributes (Python)
- Use ```data_mng\attrs\c*-*.py``` for Caravan-GAGES2 OR Caravan-only gauges 
- Use ```data_mng\attrs\g*-*.py``` for GAGES2-only gauges 

### 4. Run RF experiments (R)

#### To start with a small-scale experiment or for debugging
We recommend using ```random_forest\configs\{os_name}\config_test.yml```. This YAML file defines the configuration for a very small-scale experiment (e.g., selected signatures and attributes, with a small number of trees and grid points). After editing the configuration file, run the RF model using ```random_forest\main_serial.R```.

#### For automated training at large scale
Once you are familiar with the workflow, use the automated workflow to train an RF model regionally or at continental scale for multiple signatures.
- Prepare config files in ```random_forest\configs\{os_name}``` 
    - ```random_forest\configs\generate_config_by_cluster.py``` helps to generate config files per climate cluster
- Run the code
    - For Windows, 
    ```
    cd random_forest
    train_run.bat
    ```
    - For Linux,
    ```
    cd random_forest
    train_run.sh
    train_run_Wu.sh
    ```
- Visualization code is available in ```random_forest\visualize```

- Note that these bash or shell scripts are set up to run the multiprocessing code ```main_mp.R```. To run in non-multiprocessing (serial) mode, use ```main_serial.R``` instead. Also uncomment the following lines so the code can read the input argument: 
    ```
    args <- commandArgs(trailingOnly = TRUE)
    config_file <- args[1]
    ```
    And comment out the following lines: 
    ```
    config_file <- "./random_forest/configs/win/config_test.yml"

    if (!file.exists(config_file)) {
    stop("Configuration file not found: ", config_file)
    }

    config <- yaml::read_yaml(config_file)
    ```

#### Climate region definition
- Climate regions are currently generated using `data_mng\attrs\c3-attrs_climate_cluster.py`
- Use `random_forest\configs\linux\config_cluster_{cluster_number}.yml` for random forest
- Use `random_forest\visualize\plot_experiments_cluster.py` for visualizing RF results

#### For predicting signatures using a trained model
- Use ```random_forest\pred_main_serial.R``` and ```random_forest\pred_run.bat```
- The input attribute files must have the same column names used in the training. Refer to ```data_mng\attrs\c4-attrs_for_RF_prediction.py``` and ```data_mng\attrs\g3-attrs_equiv_for_RF_prediction.py``` to create such attribute files. 
- You must specify the directory of the trained model and the path to the input attribute file in the configuration (e.g., ```random_forest\configs\win\config_pred_gg2_only.yml```). 

### 5. Derive process inference (Python)
- Visualization code is available in ```signatures\visualize``` and ```random_forest\visualize```, as well as in ```plotting```. 
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process_single_source.py``` and ```signatures\visualize\plot_sigs_process_multiple_sources.py```
- Visualize the RF results using ```random_forest\visualize\plot_experiments_cluster.py``` to investigate the drivers of signatures

## Citation
> Araki, R., Holt, A., Hammond, J. C., Husic, A., Coxon, G., and McMillan, H. K. (2026). Continental-scale prediction of hydrologic signatures and processes, Hydrology and Earth System Sciences (In Press)

## Reference
- We drew extensively on the ideas and code of Holt, A. (2024):
    > Holt, A., & McMillan, H. (2025). New predictors for hydrologic signatures: Wetlands and geologic age across continental scales. Hydrological Processes, 39(2). https://doi.org/10.1002/hyp.70080 
  - Codebases
    > https://github.com/annieholt/Baseflow_Signature_Prediction
    > https://github.com/annieholt/Wetland_GeologicAge_Attributes

- Our ecoregion experiment ideas are inspired by Hammond et al., 2021: 
    > Hammond, J. C., Zimmer, M., Shanafield, M., Kaiser, K., Godsey, S. E., Mims, M. C., et al. (2021). Spatial patterns and drivers of nonperennial flow regimes in the contiguous United States. Geophysical Research Letters, 48(2). <https://doi.org/10.1029/2020gl090794>
- We use a modified version of the [TOSSH toolbox](https://github.com/TOSSHtoolbox/TOSSH) (Gnann et al., 2021) to calculate signatures. The custom TOSSH code is located in [https://github.com/RY4GIT/TOSSH]
    > Gnann, S.J., Coxon, G., Woods, R.A., Howden, N.J.K., McMillan H.K., 2021. TOSSH: A Toolbox for Streamflow Signatures in Hydrology. Environmental Modelling & Software. https://doi.org/10.1016/j.envsoft.2021.104983