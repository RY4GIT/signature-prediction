#!/bin/bash

# Set the date
date="20250517"

# Set the base directory path
base_dir="/home/raraki/data/signature-prediction/out/rf"

# Move to the base directory
cd "$base_dir" || { echo "Base directory not found!"; exit 1; }

# Find all directories matching the pattern and zip them
for folder in output_raraki_${date}_*; do
    # Check if it's a directory
    if [ -d "$folder" ]; then
        zip -r "${folder}.zip" "$folder"
        echo "Zipped $folder into ${folder}.zip"
    fi
done

echo "Zipping complete!"