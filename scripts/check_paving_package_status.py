"""
check_paving_package_status.py
------------------

This script runs the the individual paving 
package reporting scripts sqeuentially.
This script does NOT run the cleanup script - 
that should be run seperately after results are checked.

"""

import import_oracle, scrape_packages, compare_packages, map_packages

print("Importing from Oracle")
exec(open(import_oracle.py).read())
print("Scraping Packages")
exec(open(scrape_packages.py).read())
print("Compating Packages")
exec(open(compare_packages.py).read())
print("Mapping Packages")
exec(open(map_packages.py).read())
print("Complete")