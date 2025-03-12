# Script to execute Random Forest models, predicting hydrologic signatures based on catchment attribute datasets
# This code runs Random Forest in a parallel computing mode

#!/bin/bash

# cd random_forest/
# ./run.sh
# parallel --jobs 2 Rscript main_serial.R ::: $config_dir/config_ecoregion_{5..6}.yml

project_dir="/home/raraki/signature-prediction/random_forest"
config_dir="$project_dir/configs/linux"


# List of cluster codes
clusters="0 1 2 3 4 5"

# # Loop through each ecoregion code
for i in $clusters
do
    echo "Running experiment with $config_dir/config_cluster_$i.yml"
    Rscript main_mp.R "$config_dir/config_cluster_$i.yml"
    echo "Experiment with $config_dir/config_cluster_$i.yml finished"
done

# echo "Running experiment with $config_dir/config_test.yml"
# Rscript main_serial.R "$config_dir/config_test.yml"
# echo "Experiment with $config_dir/config_test.yml finished"

# echo "Running experiment with $config_dir/config_20250311_east.yml"
# Rscript main_serial.R "$config_dir/config_20250311_east.yml"
# echo "Experiment with $config_dir/config_20250311_east.yml finished"

# echo "Running experiment with $config_dir/config_20250311_equiv_recalc.yml"
# Rscript main_serial.R "$config_dir/config_20250311_equiv_recalc.yml"
# echo "Experiment with $config_dir/config_20250311_equiv_recalc.yml finished"

# echo "Running experiment with $config_dir/config_20250311_north.yml"
# Rscript main_serial.R "$config_dir/config_20250311_north.yml"
# echo "Experiment with $config_dir/config_20250311_north.yml finished"

# # For test
# echo "Running experiment with $config_dir/config_test.yml"
# Rscript main_mp.R "$config_dir/config_test.yml"
# echo "Experiment with $config_dir/config_test.yml finished"



# echo "Running experiment with $config_dir/config_ecoregion_11.yml"
# Rscript main_mp.R "$config_dir/config_ecoregion_11.yml"
# echo "Experiment with $config_dir/config_ecoregion_11.yml finished"


# for i in {5..13}
# do
#     echo "Running experiment with $config_dir/config_ecoregion_$i.yml"
#     Rscript main_mp.R "$config_dir/config_ecoregion_$i.yml"
#     echo "Experiment with $config_dir/config_ecoregion_$i.yml finished"
# done