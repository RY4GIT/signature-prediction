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
- Download Caravan and original CAMELS datasets
    - https://zenodo.org/records/10968468
    - https://gdex.ucar.edu/dataset/camels.html

### 2. Calculate hydrologic signatures and attributes
- Calculate signatures using ```signatures\main.m```
- Calculate wetland and geologic attributes (Holt et al., 2024), get ecoregion attributes, and assemble all the attributes by following instructions in  ```Wetland_GeologicAge_Attributes``` repo

### 3. Prepare training dataset and input attributes for RF
- Calculate statistics about Hysets data and get qualtiy flags using ```data_mng\check_hysets_qa.py```
- Mask out the signature output calculated in Step #2 using the data quality flags using ```data_mng\filt_sig_for_RFtrain.py```. This removes following gauges from the signature output file:
    - Data with inadequate duration (<5yrs) and too many nan data (>30%)
    - Gauge location with snow-dominated region based on lat/lon (still in development)
    - Overlapping gauge with CAMEL's watershed, based on the gauge_id

The following gauges are already removed at the stage of calculating attributes:
- Non-US gauges

### 4. Run RF experiment 
- Prepare config files in ```random_forest\configs``` 
    - ```random_forest\configs\generate_config_by_ecoregion.py``` helps to generate config files
- Run the code ```random_forest\run.bat``` or ```random_forest\run.sh``` depending on the OS
- For linux, 
    ```
    cd random_forest
    ./run.sh
    ```

### 5. Derive process inference
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process.py```
- Visualize the RF results using ```random_forest\visualize\plot_ecoregion_experiment.py```

## Reference
- We extensively used the ideas and codes of Holt, A. (2024):
    Holt, A. (2024). New predictors for hydrologic signatures: Wetlands and geologic age across continental scales (Order No. 31483645). Available from ProQuest Dissertations & Theses Global: The Humanities and Social Sciences Collection; ProQuest One Academic. (3083407273). Retrieved from http://libproxy.sdsu.edu/login?url=https://www.proquest.com/dissertations-theses/new-predictors-hydrologic-signatures-wetlands/docview/3083407273/se-2

- We use modified version of [TOSSH toolbox](https://github.com/TOSSHtoolbox/TOSSH) (Gnann et al., 2022) for calculating signature