# Load the list of packages from the file
package_list <- readLines("random_forest/packages.txt")

# Install packages if they are not already installed
installed_packages <- rownames(installed.packages())
packages_to_install <- package_list[!package_list %in% installed_packages]
if (length(packages_to_install) > 0) {
  install.packages(packages_to_install)
}

# Optionally, load the packages into the session
lapply(package_list, library, character.only = TRUE)

#### To run this
#### source("r/install_pckg.R")
