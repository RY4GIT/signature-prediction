# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

#!/bin/bash

# cd random_forest/
# ./run.sh
# parallel --jobs 2 Rscript main_serial.R ::: $config_dir/config_ecoregion_{5..6}.yml

project_dir="/home/raraki/signature-prediction/random_forest"
config_dir="$project_dir/configs/linux"

echo "Running experiment with $config_dir/config_gages2exp_baseline_allcaravan_withoutsnow.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_baseline_allcaravan_withoutsnow.yml"
echo "Experiment with $config_dir/config_gages2exp_baseline_allcaravan_withoutsnow.yml finished"

echo "Running experiment with $config_dir/config_gages2exp_baseline_withoutsnow.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_baseline_withoutsnow.yml"
echo "Experiment with $config_dir/config_gages2exp_baseline_withoutsnow.yml finished"

echo "Running experiment with $config_dir/config_gages2exp_gages2attrs_withoutsnow.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_gages2attrs_withoutsnow.yml"
echo "Experiment with $config_dir/config_gages2exp_gages2attrs_withoutsnow.yml finished"

echo "Running experiment with $config_dir/config_gages2exp_gages2attrs.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_gages2attrs.yml"
echo "Experiment with $config_dir/config_gages2exp_gages2attrs.yml finished"

echo "Running experiment with $config_dir/config_gages2exp_surfacewater.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_surfacewater.yml"
echo "Experiment with $config_dir/config_gages2exp_surfacewater.yml finished"

echo "Running experiment with $config_dir/config_gages2exp_bestattrs_and_surfacewater.yml"
Rscript main_mp.R "$config_dir/config_gages2exp_bestattrs_and_surfacewater.yml"
echo "Experiment with $config_dir/config_gages2exp_bestattrs_and_surfacewater.yml finished"


# # For test
# echo "Running experiment with $config_dir/config_test.yml"
# Rscript main_mp.R "$config_dir/config_test.yml"
# echo "Experiment with $config_dir/config_test.yml finished"

# # List of ecoregion codes
# ecoregions="11 1210 6713 81 82 91 92"

# # # Loop through each ecoregion code
# for i in $ecoregions
# do
#     echo "Running experiment with $config_dir/config_ecoregion_$i.yml"
#     Rscript main_mp.R "$config_dir/config_ecoregion_$i.yml"
#     echo "Experiment with $config_dir/config_ecoregion_$i.yml finished"
# done

# echo "Running experiment with $config_dir/config_ecoregion_11.yml"
# Rscript main_mp.R "$config_dir/config_ecoregion_11.yml"
# echo "Experiment with $config_dir/config_ecoregion_11.yml finished"


# for i in {5..13}
# do
#     echo "Running experiment with $config_dir/config_ecoregion_$i.yml"
#     Rscript main_mp.R "$config_dir/config_ecoregion_$i.yml"
#     echo "Experiment with $config_dir/config_ecoregion_$i.yml finished"
# done