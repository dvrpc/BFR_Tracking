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

# delete shapefiles and GeoJSONs?
