"""
package_revision.py
------------------

This script allows users to update status reports
and mapped outputs as PennDOT sends revisions to
paving packages. 

USERS MUST MANUALLY UPDATE CSV files with the revisions.

This script is similar to the full check_paving_package_status.py
but does not include scrape_packages.py

"""
from import_oracle import main as importer
from update_db_with_revision import main as updater
from map_packages import main as mapper
from make_folium_map import main as webmapper

print("Importing from Oracle")
importer()
print("Updating SQL tables")
updater()
print("Comparing and Mapping Paving Package Segments")
mapper()
print("Rendering Webmap")
webmapper()
print("Complete!")
