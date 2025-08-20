#!/bin/bash
# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

# cd random_forest/
# ./train_run.sh

# To change the permission
# chmod +x train_run.sh

# To run in the background, use 
# nohup ./train_run.sh > experiment.log 2>&1 &

# To stop the background process, use
# pkill -f "train_run.sh"
# Or, 
# kill {PID}

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


# Run all clusters
run_experiment "config_cluster_all_Wu"