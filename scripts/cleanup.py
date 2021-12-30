"""
cleanup.py
------------------

This script drops database tables related to paving packages. 
It also deleted interim CSV files created via scrape_packages,
located in paving_packages/CSV.

"""
import env_vars as ev
from env_vars import ENGINE
from sqlalchemy import create_engine
from pathlib import Path
import os
import shutil

data_folder = Path(ev.DATA_ROOT)
raw_packages = data_folder / "paving_package/PDFs"

# delete postgres db tables related to packages
connection = ENGINE.raw_connection()
cursor = connection.cursor()

sql = """ DROP TABLE IF EXISTS %s; """

for filepath in raw_packages.rglob("*.pdf"):
    cursor.execute(sql, filepath.stem)

# delete interim CSV files
for p in Path(fr"{ev.DATA_ROOT}\paving_package\CSVs").rglob("*.csv"):
    try:
        p.unlink()
    except OSError as e:
        print("Error: %s : %s " % (p, e.strerror))

# archive reports, shapefiles, and geojsons
# one previous iteration of the output files remain
shapes_source = fr"{ev.DATA_ROOT}\shapefiles\\"
geojson_source = fr"{ev.DATA_ROOT}\geojson\\"
report_source = fr"{ev.DATA_ROOT}\paving_package\Reports\\"
pdf_source = fr"{ev.DATA_ROOT}\paving_package\PDFs\\"

archive_path = "D:\dvrpc_shared\BFR_Tracking\archive"
shapes_dest = fr"{archive_path}\shapefiles\\"
geojson_dest = fr"{archive_path}\geojson\\"
report_dest = fr"{archive_path}\paving_package\Reports\\"
pdf_dest = fr"{archive_path}\paving_package\PDFs\\"

folder_list = ["shapes", "geojson", "report", "pdf"]

# fetch all files
for folder in folder_list:
    source_folder = folder + "_source"
    destination_folder = folder + "_dest"
    for file_name in os.listdir(source_folder):
        # construct full file path
        source = source_folder + file_name
        destination = destination_folder + file_name
        # move only files
        if os.path.isfile(source):
            shutil.move(source, destination)
            print("Moved:", file_name)
