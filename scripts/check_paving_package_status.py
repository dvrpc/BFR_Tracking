"""
check_paving_package_status.py
------------------

This script runs the the individual paving 
package reporting scripts sqeuentially.
This script does NOT run the cleanup script - 
that should be run seperately after results are checked.

"""
from import_oracle import main as importer
from scrape_packages import main as scrape
from map_packages import main as mapper
from make_folium_map import main as webmapper

print("Importing from Oracle")
importer()
print("Scraping Paving Packages")
# do not re-scrape packages that have been revised. Instead, use package_revision.py
# scrape()
print("Comparing and Mapping Paving Package Segments")
mapper()
print("Rendering Webmap")
webmapper()
print("Complete!")
