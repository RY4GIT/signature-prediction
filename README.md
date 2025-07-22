# signature-prediction
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![CodeStyle](https://img.shields.io/badge/code%20style-Ruff%20and%20Air-black)]()

Scripts to calculate hydrologic signatures, running TOSSH Toolbox functions, and to predict hydrologic signatures using random forest modeling. 

Extending the work by [Holt & McMillan (2025)](https://doi.org/10.1002/hyp.70080). This repository was originally a folk of the one created by Anne Holt: https://github.com/annieholt/Baseflow_Signature_Prediction

## Directory layout
### Github layout
    ├── data_mng                # Data management
    ├── figures                 # Visualization codes for manuscripts and conference posters. 
    ├── random_forest           # Script to run random forest
    ├── refs                    # Reference Random Forest codes from Holt and McMillan (2025) HP, Zipper et al. (2021) ERL, and Husic (2025) preprint
    └── signatures              # Script to calculate hydrologic signature using TOSSH toolbox


## Getting started
If you have downloaded finalized dataset (signature values, landscape attributes), you can skip to the Step 5: Derive process inference.  

### 1. Preparation
- Folk and clone the following repos
    ```
    git clone https:\\github.com\RY4GIT\signature-prediction.git
    ```
    ```
    git clone https:\\github.com\RY4GIT\TOSSH
    ```
    ```
    git clone https:\\github.com\RY4GIT\Wetland_GeologicAge_Attributes.git
    ```
- Download Caravan v1.5 dataset
    - <https:\\zenodo.org\records\10968468>
- Download GAGES2 datasets
    - Landscape attributes and GIS layer: <https://www.sciencebase.gov/catalog/item/631405bbd34e36012efa304a>
    - Streamflow data: <https://doi-usgs.github.io/dataRetrieval/>
    - gridMET forcing: <https://www.sciencebase.gov/catalog/item/6414b3f9d34eb496d1ceb5ae>
        - Use `data_mng\hydroclimatic_timeseries\curate_gages2.py` to combine gridMET and streamflow data
-Set up Environments
    - Python environment: `environment_minimal.yml` or `environment.yml` (Set up for Win)
    - R environment: `random_forest\envs`
    - Matlab ver: tested on 2020b-2024b

### 2. Calculate signatures and attributes 
#### 2.1. Calculate hydrologic signatures (Matlab)
- Calculate signatures using:  
    - ```signatures\main_caravan.m``` for Caravan dataset
    - ```signatures\main_gages2_gridmet.m``` for GAGES2 dataset
    - (experimental) ```signatures\main_gages2_swi.m``` for GAGES2 dataset with surface input dataset from [Hammond, 2024](https://www.sciencebase.gov/catalog/item/6494515fd34ef77fcb014eb0)

#### 2.1 Calculate additional landscape attributes (Python)
- Calculate additional attributes, wetland fraction and geologic ages (Holt and McMillan, 2025) following instructions (step 1-3) in  [```Wetland_GeologicAge_Attributes```](https://github.com/RY4GIT/Wetland_GeologicAge_Attributes) repo


### 3. Prepare input and evaluation datasets for Random Forest model
#### 3.1. Curate signature files (Python)
- Get data qualtiy flags using ```data_mng\hydroclimatic_timeseries\qa_hysets.py``` and ```data_mng\hydroclimatic_timeseries\qa_gages2.py```
- Filter out some gauges and signatures using scripts in ```signatures\postprocess\```
    - `signatures\postprocess\postprocess_caravan_sigs_for_RF.py` for Caravan dataset
    - `signatures\postprocess\postprocess_gages2_gridMET_sigs.py` for GAGES2 dataset
    - These scripts copy signature files with extension `_filt_qc.csv` (for meeting conditions 1 & 2), `_filt_qc_snow.csv` (for meeting conditions 1 & 2 & 3), and `_filt_qc_snow_area.csv` (for meeting conditions 1 & 2 & 3 & 4)
        1. Exclude Hysets watersheds with bad data quality (less than 5 years of record OR >30\% record is NaN for the period where data is available)
        2. Exclude Hysets watersheds overlapping with CAMELS OR Exclude GAGES2 watersheds overlapping with Caravan
        3. Event-based overlandflow signatures, exclude Caravan and GAGES2 watersheds dominated with snow with `frac_snow` >20\%
        4. Exclude Caravan watersheds that has >25% error in estimated watershed drainage area between Caravan and GAGES-II estimates (consisting of 31 watersheds)
#### 3.2. Curate landscape attributes (Python)
- Use ```data_mng\attrs\c*-*.py``` for Caravan-GAGES2 OR Caravan-only gauges 
- Use ```data_mng\attrs\g*-*.py``` for GAGES2-only gauges 

### 4. Run RF experiment (R script)

#### To start off some small-scale experiment or debugging
I recommend using the ```random_forest\configs\{os_name}\config_test.yml```. This YML file defines configuration for very small-scale experiment (e.g., only for selected signatures and attributes, with small number of trees and grids). After editing the configuration file, try running the RF model using ```random_forest\main_serial.R```. 

#### For an automated training for large-scale experiments
Once you get the hang of it, use automated workflow for training RF model regionally or at continental-scale for multiple signatures.
- Prepare config files in ```random_forest\configs\{os_name}``` 
    - ```random_forest\configs\generate_config_by_cluster.py``` helps to generate config files per climate cluster
- Run the code
    - For Windows, 
    ```
    cd random_forest
    train_run.bat
    ```
    - For linux, 
    ```
    cd random_forest
    train_run.sh
    ```
- Visualization code available at ```random_forest\visualize```

- Note that these bash or shell files are set up to run the multi-processing code ```main_mp.R```. If you want to run in non-multiprocessing (serial) mode, use ```main_serial.R``` instead. Also de-comment the following lines, so that to allow the code to read the input argument: 
    ```
    args <- commandArgs(trailingOnly = TRUE)
    config_file <- args[1]
    ```
    And comment-out the following lines: 
    ```
    config_file <- "./random_forest/configs/win/config_test.yml"

    if (!file.exists(config_file)) {
    stop("Configuration file not found: ", config_file)
    }

    config <- yaml::read_yaml(config_file)
    ```

####  Climate region definition
- Climate regions is currently generated using `data_mng\attrs\c3-attrs_climate_cluster.py`
- Use `random_forest\configs\linux\config_cluster_{cluster_number}.yml` for random forest
- Use `random_forest\visualize\plot_experiments_cluster.py` for visualizing RF results

#### For predicting signature using trained model
- Use ```random_forest\pred_main_serial.R``` and ```random_forest\pred_run.bat```
- The input attribute files must have the same column names used in the training. Refer to ```data_mng\attrs\c4-attrs_for_RF_prediction.py``` and ```data_mng\attrs\g3-attrs_equiv_for_RF_prediction.py``` to create such attribute files. 
- You have to specify the directory of the trained model and input attribute file path in the configuration (e.g., ```random_forest\configs\win\config_pred_gg2_only.yml```). 

### 5. Derive process inference (Python)
- Visualization code available at ```signatures\visualize``` and ```random_forest\visualize```, as well as in ```plotting```. 
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process_single_source.py``` and ```signatures\visualize\plot_sigs_process_multiple_sources.py```
- Visualize the RF results using ```random_forest\visualize\plot_experiments_cluster.py``` to investigate on the drivers of signatures


## Reference
- We extensively used the ideas and codes of Holt, A. (2024):
    > Holt, A., & McMillan, H. (2025). New predictors for hydrologic signatures: Wetlands and geologic age across continental scales. Hydrological Processes, 39(2). https://doi.org/10.1002/hyp.70080
    > https://github.com/annieholt/Baseflow_Signature_Prediction
    > https://github.com/annieholt/Wetland_GeologicAge_Attributes

- Our ecoregion experiment ideas are inspired by Hammond et al., 2021: 
    > Hammond, J. C., Zimmer, M., Shanafield, M., Kaiser, K., Godsey, S. E., Mims, M. C., et al. (2021). Spatial patterns and drivers of nonperennial flow regimes in the contiguous United States. Geophysical Research Letters, 48(2). <https://doi.org/10.1029/2020gl090794>
- We use modified version of [TOSSH toolbox](https:\\github.com\TOSSHtoolbox\TOSSH) (Gnann et al., 2022) for calculating signatures. The custom TOSSH codes are located in <https:\\github.com\RY4GIT\TOSSH>