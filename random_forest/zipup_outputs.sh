#!/bin/bash

# Set the date
date="20250429"

# Set the base directory path
base_dir="/home/raraki/data/signature-prediction/out/rf"

# Loop over 0 to 5
for n in {0..5}; do
    folder="${base_dir}/output_raraki_${date}_cluster_${n}"
    if [ -e "$folder" ]; then
        zip -r "${folder}.zip" "$folder"
        echo "Zipped $folder into ${folder}.zip"
    else
        echo "Warning: $folder does not exist, skipping."
    fi
done

# Now zip the 'all' folder
folder="${base_dir}/output_raraki_${date}_cluster_all"
if [ -e "$folder" ]; then
    zip -r "${folder}.zip" "$folder"
    echo "Zipped $folder into ${folder}.zip"
else
    echo "Warning: $folder does not exist, skipping."
fi
