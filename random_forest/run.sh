#!/bin/bash

# # For test
# echo "Running experiment with $config_dir/config_test.yml"
# Rscript main_mp.R "$config_dir/config_test.yml"
# echo "Experiment with $config_dir/config_test.yml finished"

# parallel --jobs 2 Rscript main_serial.R ::: $config_dir/config_ecoregion_{5..6}.yml

# echo "Running experiment with $config_dir/config_caravan_us.yml"
# Rscript main_mp.R "$config_dir/config_caravan_us.yml"
# echo "Experiment with $config_dir/config_caravan_us.yml finished"

project_dir="/home/raraki/signature-prediction/random_forest"
config_dir="$project_dir/configs/linux"

for i in {5..13}
do
    echo "Running experiment with $config_dir/config_ecoregion_$i.yml"
    Rscript main_mp.R "$config_dir/config_ecoregion_$i.yml"
    echo "Experiment with $config_dir/config_ecoregion_$i.yml finished"
done