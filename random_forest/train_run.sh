#!/bin/bash
# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

# cd random_forest/
# ./train_run.sh
# parallel --jobs 2 Rscript train_main_serial.R ::: $config_dir/config_ecoregion_{5..6}.yml

project_dir="/home/raraki/signature-prediction/random_forest"
config_dir="$project_dir/configs/linux"

# Function to run an experiment with a given config
run_experiment() {
    local config_name="$1"
    local config_path="$config_dir/$config_name.yml"
    
    echo "Running experiment with $config_path"
    Rscript train_main_mp.R "$config_path"
    echo "Experiment with $config_path finished"
    echo "----------------------------------------"
}

# Run experiments for individual clusters
for i in 0 1 2 3 4 5; do
    run_experiment "config_cluster_$i"
done

# Define configs as space-separated string instead of array for better sh compatibility
configs="config_cluster_all config_20250517_baseline config_20250517_camels config_20250517_gages2_attrs config_20250517_gages2_ref config_20250517_gages2"

# Loop through configs
for config in $configs; do
    run_experiment "$config"
done
