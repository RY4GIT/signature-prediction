# signature-prediction
Scripts to calculate hydrologic signatures, running TOSSH Toolbox functions, and to predict hydrologic signatures using random forest modeling. Extending [the work by Anne Holt](https://github.com/annieholt/Baseflow_Signature_Prediction)


## Directory layout
    ├── aholt_codes             # Codes from annieholt repo
    ├── data_mng                # Script for Caravan data visualization and quality control
    ├── random_forest           # Script to run random forest
    └── signatures              # Script to calculate hydrologic signature using TOSSH toolbox

## Getting started
### 1. Folk modified TOSSH toolbox
```
git clone https://github.com/RY4GIT/TOSSH
```

## Reference
- We use modified version of [TOSSH toolbox](https://github.com/TOSSHtoolbox/TOSSH) (Gnann et al., 2022) for calculating signature