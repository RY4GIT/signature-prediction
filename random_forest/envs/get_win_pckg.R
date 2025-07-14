# Get versions of required packages
packages <- c(
    "tidyverse",
    "randomForest",
    "caret",
    "doParallel",
    "dplyr",
    "foreach",
    "yaml",
    "iml",
    "data.table"
)

# Get installed package information
installed_info <- installed.packages()[packages, c("Package", "Version")]

# Create a data frame with package info
pkg_versions <- data.frame(
    Package = installed_info[, "Package"],
    Version = installed_info[, "Version"],
    stringsAsFactors = FALSE
)

# Print the versions
print(pkg_versions)

# Create installation commands for Linux
install_commands <- paste0(
    'devtools::install_version("',
    pkg_versions$Package,
    '", version = "',
    pkg_versions$Version,
    '", repos = "https://cran.rstudio.com/")'
)

# Print installation commands
cat("Run these commands on Linux:\n")
cat(paste(install_commands, collapse = "\n"))

# Save to file
write.csv(
    pkg_versions,
    "./random_forest/envs/package_versions.csv",
    row.names = FALSE
)
writeLines(install_commands, "./random_forest/envs/install_commands.R")
