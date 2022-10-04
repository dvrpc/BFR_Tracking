# BFR_Tracking

Program tracking database tools

## Environment Setup

To create the python environment, run the next line in a conda prompt from the project directory:

```
conda env create -f environment.yml
```

To activate the new environment, run the following line:

```
conda activate bfr_tracking
```

To update the environment as changes are needed, run the following line:

```
conda env update -f environment.yml
```

## File Organization

Upon receipt of new paving packages from PennDOT, save the PDF tables in: `BFR/Tracking/data/paving_package/PDFs`.

PDF files names should remain unchanged and in the following format: `Location Summary A##` where `A` represents the first letter of the county name

Report CVSs are saved in: `BFR/Tracking/data/paving_package/Reports`

Output shapefiles are saved: `BFR/Tracking/data/paving_package/shapefiles`

## Order of Operations

`check_paving_package_status.py` runs the other scripts necessary to compare a new set of paving packages with the database records. Scripts are run in the following order:

- `import_oracle.py`: gathers latest record information from Oracle tracking database and sets up in postgres for analysis
- `import_filters.py`: creates status field based on current standing of each record in the review process; requires manual output from oracle DB
- `scrape_packages.py`: pulls data from paving package PDFs shared by PennDOT and imports into postgres for analysis
- `map_packages.py`: creates shapefiles/geojsons from paving package data
- `make_folium_map.py`: maps the paving packages for visual comparison

## Running Scripts

To run any of the scripts in this repo, activate the conda environment, change directory to the project folder, and then run the `python` command followed by the path to the file. For example:

```
conda activate bfr_tracking
d:
cd dvrpc_shared/BFR_Tracking
python scripts/{script_name}.py
```

## Handling Paving Package Revisions

PennDOT often sends revisions after the initial paving package is distributed. Since revisions, although minor, often change the format of the PDF tables, the best way to handle them is to manually update the interim CSV's located here:

```
D:\dvrpc_shared\BFR_Tracking\data\paving_package\CSVs
```

Once updated and saved, run `package_revision.py` to update the report and map. This script is a subset of `check_paving_package_status.py` that bypasses the PDF scraping step and uses the manually modified CSV.

To keep track of which revisions have been incorporated, a google sheet is available here:

```
https://docs.google.com/spreadsheets/d/1JgnZVrL4ZxedgYVyf9-Vw6cHpRy1d4zSgO7_c0eoPSY/edit?usp=sharing
```

## Handling failed PDF scrapes

See `troubleshoot_scrape.py`

## Cleanup Script

To keep the postgres database manageable, run `cleanup.py` after the comparison and mapping are complete. Database tables related to specific paving packages will dropped. Interim CSV's will also be deleted. Output reports, shapefiles, and geojson files will be archived.
