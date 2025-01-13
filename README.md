# signature-prediction
Scripts to calculate hydrologic signatures, running TOSSH Toolbox functions, and to predict hydrologic signatures using random forest modeling. Extending [the work by Anne Holt](https:\\github.com\annieholt\Baseflow_Signature_Prediction)


## Directory layout
    ├── refs                    # Reference codes from annieholt and dry-rivers-rcn repo
    ├── data_mng                # Script for Caravan data visualization and quality control
    ├── plotting                # Contains some plotting codes for manuscripts \ conference poster etc.
    ├── random_forest           # Script to run random forest
    └── signatures              # Script to calculate hydrologic signature using TOSSH toolbox

### Google Drive Layout (for collaborators)
```
    ├── data                    # Contains data
    ├── docs                    # Contains manuscript draft, AGU poster files, my thought process to determine attributes and signatures of interest (Excel files) 
    ├── gis                     # Contains GIS layers
    ├── out                     # Contains analysis outputs
    └── refs                    # Slipbox to put some references (not well organized)
```
#### Highlights: 
- Randome Forest results are stored in ```Signatures -- large scale\baseflow\RAraki\out\rf```
- Signature value are stored in ```Signatures -- large scale\baseflow\RAraki\out\signatures```
- Landscape attributes are stored in ```Signatures -- large scale\baseflow\RAraki\data\derived_attrs```

## Getting started (for collaborators, those who already have access to the Google Drive)
### 1. Preparation
- Folk and clone following repo
    ```
    git clone https:\\github.com\RY4GIT\signature-prediction.git
    ```
- Make sure you have access to the Google Shared Drive folder ```Signatures -- large scale\baseflow\RAraki``` on your desktop
- If you don't have a Google Drive Desktop, download all contents from the following directory
     - ```Signatures -- large scale\baseflow\RAraki\data```
     - ```Signatures -- large scale\baseflow\RAraki\out\signatures``` (if you want to skip signature calculation part)

### 2. Calculate hydrologic signatures (Matlab)
Skip this step if you have downloaded pre-caluclated signature values from ```Signatures -- large scale\baseflow\RAraki\out\signatures```
- Folk and clone following repo
    ```
    git clone https:\\github.com\RY4GIT\TOSSH
    ```
- Calculate signatures using ```.\signatures\main.m```
- Some visualization code available at ```.\signatures\visualize```

### 3. Run RF experiment (R script)
#### To start off some small-scale experiment or implement debug
To start off, I recommend using the ```.\random_forest\configs\win\config_test.yml```. This YML file defines configuration for very small-scale experiment (only for selected signatures and attributes, with small number of trees and grids). After editing the configuration file, try running the RF model using ```.\random_forest\main_serial.R```. 

#### For an automated workflow
Once you get the hang of it, you might want to automate the workflow because you have to run the code for multiple ecoregions and multiple signatures.
- Prepare config files in ```.\random_forest\configs\{your OS name}``` 
    - ```.\random_forest\configs\generate_config_by_ecoregion.py``` helps to generate config files per ecoregion
- Run the code ```.\random_forest\run.bat``` or ```.\random_forest\run.sh``` depending on the OS. 
    - For Windows, 
    ```
    cd random_forest
    run.bat
    ```
    - For linux, 
    ```
    cd random_forest
    .\run.sh
    ```

- Note that these bash or shell files are set up to points to the multi-processing code ```main_mp.R```. If you want to run in non-multiprocessing (serial) mode, replace it with ```main_serial.R``` and also de-comment the following lines, so that to allow the code to read the input argument.: 
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

- Some visualization code available at ```.\random_forest\visualize```

### 4. Derive process inference (Python)
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process.py```
- Visualize the RF results using ```random_forest\visualize\plot_ecoregion_experiment.py``` to investigate on predictability and drivers of signatures

### 5 (Optional). Change Ecoregion subsetting definitions (ArcGIS + Python)
- Folk and clone following repos
    ```
    git clone https:\\github.com\RY4GIT\Wetland_GeologicAge_Attributes.git
    ```
- xxxx on ArcGIS (Note: I tried to do this using Python GeoPandas and somehow didn't work well)
- adjust
- assemble

#### Ecoregion definition 
There are multiple ecoregion definition that I've tried out. The followings are the definitions & attribute files that has the corresponding ecoregion column. 
- EPA Level x ecoregion definition

- Hammond et al., 2011 definition 

- Hammond et al., 2011 definition + further aggregating some regions


## [Still in edit] Instructions reproduce the entire work flow, including attribute generation
### 1. Preparation
- Folk and clone following repos
    ```
    git clone https:\\github.com\RY4GIT\signature-prediction.git
    ```
    ```
    git clone https:\\github.com\RY4GIT\TOSSH
    ```
    ```
    git clone https:\\github.com\RY4GIT\Wetland_GeologicAge_Attributes.git
    ```
- Download Caravan and original CAMELS datasets
    - https:\\zenodo.org\records\10968468
    - https:\\gdex.ucar.edu\dataset\camels.html

### 2. Calculate hydrologic signatures and attributes
- Calculate signatures using ```signatures\main.m```
- Calculate wetland and geologic attributes (Holt et al., 2024), get ecoregion attributes, and assemble all the attributes by following instructions in  ```Wetland_GeologicAge_Attributes``` repo

### 3. Prepare training dataset and input attributes for RF
- Calculate statistics about Hysets data and get qualtiy flags using ```data_mng\check_hysets_qa.py```
- Mask out the signature output calculated in Step #2 using the data quality flags using ```data_mng\filt_sig_for_RF.py```. This removes following gauges from the signature output file:
    - Data with inadequate duration (<5yrs) and too many nan data (>30%)
    - Gauge location with snow-dominated region based on lat\lon (still in development)
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
    .\run.sh
    ```

### 5. Derive process inference
- Visualize the signature patterns using ```signatures\visualize\plot_sigs_process.py```
- Visualize the RF results using ```random_forest\visualize\plot_ecoregion_experiment.py``` to investigate on predictability and drivers of signatures

## Reference
- We extensively used the ideas and codes of Holt, A. (2024):
    Holt, A. (2024). New predictors for hydrologic signatures: Wetlands and geologic age across continental scales (Order No. 31483645). Available from ProQuest Dissertations & Theses Global: The Humanities and Social Sciences Collection; ProQuest One Academic. (3083407273). Retrieved from https:\\www.proquest.com\dissertations-theses\new-predictors-hydrologic-signatures-wetlands\docview\3083407273\se-2
- Our ecoregion experiment ideas are inspired by Hammond et al., 2021: 
    Hammond, J. C., Zimmer, M., Shanafield, M., Kaiser, K., Godsey, S. E., Mims, M. C., et al. (2021). Spatial patterns and drivers of nonperennial flow regimes in the contiguous United States. Geophysical Research Letters, 48(2). https://doi.org/10.1029/2020gl090794
- We use modified version of [TOSSH toolbox](https:\\github.com\TOSSHtoolbox\TOSSH) (Gnann et al., 2022) for calculating signatures. The custom TOSSH codes are located in https:\\github.com\RY4GIT\TOSSH