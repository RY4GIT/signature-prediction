# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

#!/bin/bash

# cd random_forest/
# ./train_run.sh
# parallel --jobs 2 Rscript train_main_serial.R ::: $config_dir/config_ecoregion_{5..6}.yml

project_dir="/home/raraki/signature-prediction/random_forest"
config_dir="$project_dir/configs/linux"

# List of cluster codes
clusters="0 1 2 3 4 5"

# Loop through each cluster
for i in $clusters
do
    echo "Running experiment with $config_dir/config_cluster_$i.yml"
    Rscript train_main_mp.R "$config_dir/config_cluster_$i.yml"
    echo "Experiment with $config_dir/config_cluster_$i.yml finished"
done

# For the all clusters
echo "Running experiment with $config_dir/config_cluster_all.yml"
Rscript train_main_mp.R "$config_dir/config_cluster_all.yml"
echo "Experiment with $config_dir/config_cluster_all.yml finished"
