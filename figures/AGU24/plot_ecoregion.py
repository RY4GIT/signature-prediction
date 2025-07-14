# %%
# Ecoregion data polygon
import geopandas as gpd
import os
import matplotlib.pyplot as plt

geodata_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\data"
geodata_name = "EcoRegions"
geodata_filename = "NA_CEC_Eco_Level1.shp"
geodata = gpd.read_file(os.path.join(geodata_dir, geodata_name, geodata_filename))


# %%
# Load US boundary from Natural Earth
from cartopy.io.shapereader import natural_earth

us_boundary = gpd.read_file(
    natural_earth(resolution="50m", category="cultural", name="admin_0_countries")
)
us_boundary = us_boundary[us_boundary["ADMIN"] == "United States of America"]


# %%
# Clip the ecoregions to the US boundary
geodata_clipped = gpd.clip(us_boundary, geodata)
# %%
fig, ax = plt.subplots(figsize=(12, 8))
geodata_clipped.plot(ax=ax, color="lightgrey", edgecolor="white", linewidth=1.5)

# Add a title and remove axes for better aesthetics
# ax.set_title("NA CEC EcoRegions - Level 1", fontsize=16)
ax.axis("off")
# %%

# Save the clipped map to PDF and PNG
output_dir = r"G:\Shared drives\Signatures -- large scale\baseflow\AHolt\output"
pdf_filename = os.path.join(output_dir, "Clipped_NA_CEC_EcoRegions_US_Boundary.pdf")
png_filename = os.path.join(output_dir, "Clipped_NA_CEC_EcoRegions_US_Boundary.png")

plt.savefig(pdf_filename, format="pdf", bbox_inches="tight")
plt.savefig(png_filename, format="png", dpi=300, bbox_inches="tight")

plt.show()
