# signature-prediction
Scripts to calculate hydrologic signatures, running TOSSH Toolbox functions, and to predict hydrologic signatures using random forest modeling. Extending [the work by Anne Holt](https://github.com/annieholt/Baseflow_Signature_Prediction)


## Directory layout
    ├── aholt_codes             # Codes from annieholt repo
    ├── data_mng                # Script for Caravan data visualization and quality control
    ├── random_forest           # Script to run random forest
    └── signatures              # Script to calculate hydrologic signature using TOSSH toolbox

## Getting started
### 1. Preparation
- Folk and clone following repos
    ```
    git clone https://github.com/RY4GIT/TOSSH
    ```
    ```
    git clone https://github.com/RY4GIT/Wetland_GeologicAge_Attributes.git
    ```
- 1.2. Download Caravan and CAMELS datasets

### 2. Calculate hydrologic signatures and attributes
- Calculate signatures using ```signatures\main.m```
- Calculate wetland and geologic attributes (Holt et al., 2024) and assemble all the attributes by following instructions in  ```Wetland_GeologicAge_Attributes``` repo

### 3. Prepare training dataset and input attributes for RF
- Calculate statistics about Hysets data qualtiy using ```data_mng\check_hysets_qa.py```. This removes
    - Data with inadequate duration (<5yrs) and too many nan data (>30%)
    - Gauge location with snow-dominated region based on lat/lon (still in development)
    - Overlapping gauge with CAMEL's watershed, based on the gauge_id

- Mask out the signature output calculated in Step #2 using the data quality flags using ```code is still in development```
- Get the subset flags for regional RF experiment using ```data_mng\get_caravan_ecoregion.py``` (subset region is subject to change)

### 4. Run RF experiment 
- Prepare config files in ```random_forest\configs``` 
- Run the code ```random_forest\run.bat``` or ```random_forest\run.sh``` depending on the OS

### 5. Process analysis
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process.py```
- Visualize the RF results using ```random_forest\visualize\plot_ecoregion_experiment.py```

## Reference
- We use modified version of [TOSSH toolbox](https://github.com/TOSSHtoolbox/TOSSH) (Gnann et al., 2022) for calculating signature