"""
cleanup.py
------------------

This script drops database tables related to paving packages. 
It also deleted interim CSV files created via scrape_packages,
located in paving_packages/CSV.

"""
import db_connections
from sqlalchemy import create_engine
from pathlib import Path

project_folder = Path.cwd().parent
data_folder = project_folder / "data"
raw_packages = data_folder / "paving_package/PDFs"

# delete postgres db tables related to packages
engine = create_engine(db_connections.postgres_uri)
connection = engine.raw_connection()
cursor = connection.cursor()

sql = """ DROP TABLE IF EXISTS %s; """

for filepath in raw_packages.rglob("*.pdf"):
    cursor.execute(sql, filepath.stem)
    

# delete interim CSV files
for p in Path("data\paving_package\CSVs").rglob('*.csv'):
    try:
        p.unlink()
    except OSError as e:
        print("Error: %s : %s " % (p, e.strerror))





