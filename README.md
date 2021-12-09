# BFR_Tracking

Program tracking database and eventual front end

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

## Running scripts

To run any of the scripts in this repo, activate the conda environment and then run the `python` command followed by the path to the file. For example:

```
conda activate bfr_tracking
python ./scripts/scrape_packages.py
```
