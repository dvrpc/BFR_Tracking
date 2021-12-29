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
from compare_packages import main as compare
from map_packages import main as mapper

print("Importing from Oracle")
importer()
print("Scraping Paving Packages")
scrape()
print("Comparing Pacakges to 5-year Plan")
compare()
print("Mapping Paving Package Segments")
mapper()
print("Complete!")
