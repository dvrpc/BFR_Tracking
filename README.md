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
## File Setup

Upon receipt of new paving packages from PennDOT, save the PDF tables in: ` BFR/Tracking/data/paving_package/PDFs `. 

PDF files names should remain unchanged and in the following format: `Location Summary A##` where `A` represents the first letter of the county name

Report CVSs are saved in: ` BFR/Tracking/data/paving_package/Reports `

Output shapefiles are saved: ` BFR/Tracking/data/paving_package/shapefiles `

## Running Scripts

To run any of the scripts in this repo, activate the conda environment, change directory to the project folder, and then run the `python` command followed by the path to the file. For example:

```
conda activate bfr_tracking 
d:
cd dvrpc_shared/BFR_Tracking
python /scripts/{script_name}.py
```

## Cleanup Script

To keep the postgres database manageable, run `cleanup.py` after the comparison and mapping are complete. Database tables related to specific paving packages will dropped.