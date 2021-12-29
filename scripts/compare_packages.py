"""
compare_packages.py
------------------

This script compares the output from scrape_packages.py to the SEPA data table from oracle.
It handles repeated files and files that are not in the data table and provides an updated status.
It produces a CSV report listing projects from the paving packages and their status.
A copy of the output table is also included in the database.

"""

from __future__ import annotations
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from pathlib import Path
import db_connections

def create_df_from_query(package_name):
	compare = """
	with tblA as (
	select 
		ls.project_num as Project,
		fo."GISID" ,
		fo."CALENDAR_YEAR",
		fo."ADMINSELECTED",
		fo."SOURCE" ,
		fo."CHANGECODE" ,
		ls.sr as StateRoute,
		ls."name" ,
		ls."from" ,
		ls. "to",
		ls.miles as Miles,
		fo."PLANNED" as db_miles,
		ls.muni1 as Muni1,
		ls.muni2 as Muni2,
		ls.muni3 as Muni3
	from "%s" ls 
	left join from_oracle  fo
	on cast(ls.sr AS numeric) = fo."STATE_ROUTE" 
	and cast(ls.fsegment as numeric) = fo."SEGMENT_FROM" 
	and cast(ls.tsegment as numeric) = fo."SEGMENT_TO"
	order by ls.project_num
	),
	tblB as (
	select
		Project,
		count(Project) as count
	from tblA
	group by Project 
	)
	select
		tblA.*,
		tblB.count
	from tblA
	inner join tblB
	on tblA.project = tblB.project;
	"""

	input_df = pd.read_sql(compare % package_name, con = engine)
	input_df['ReportStatus'] = np.nan

	return input_df

def flag_missing_records(df):
    missing_df = df[df['GISID'].isnull()]
    missing_df['ReportStatus'].fillna('Not Evaluated', inplace=True)

    return missing_df

def single_records(df):
    nr = df[df['count'] == 1]
    notrepeated_df = nr[nr['SOURCE'].notna()]
    #change to status eventually; once field is added
    #may need to deal with status = not screened here too
    notrepeated_df['ReportStatus'].fillna('Not Repeated', inplace=True)

    return notrepeated_df

# series of functions to address repeated records
def identify_repeats(df):
    repeat = df[df['count'] > 1]
    repeated_df =  repeat[repeat['SOURCE'].notna()]
    return repeated_df

def find_latest_source(df):
    endyears = []
    for item in df['SOURCE'].unique():
        endyears.append(int(item[-4:]))
    maxyear = max(endyears)
    return maxyear

def find_newest_repeat(df, year):
    newest_repeat = df[df['SOURCE'].str.endswith(str(year))]
    return newest_repeat

def flag_still_repeated(df):
    still_repeated = df['project'][df['project'].duplicated()].unique()
    return still_repeated

def keep_newest(df, list_of_dubs):
    touse = df[~df['project'].isin(list_of_dubs)]
    return touse

def keep_segments_from_same_year(df, list_of_dubs):
    tofix = df[df['project'].isin(list_of_dubs)]
    keepboth = tofix[tofix.duplicated(subset=['project', 'CALENDAR_YEAR'], keep=False)]
    return keepboth

def keep_only_admin_selected(df, list_of_dubs):
    tofix = df[df['project'].isin(list_of_dubs)]
    keepone = tofix[~tofix.duplicated(subset=['project', 'CALENDAR_YEAR'], keep=False)]
    kept =  keepone[keepone['ADMINSELECTED'] == 'Y']
    return kept

def rebuild_df(frame1, frame2, frame3):
    frames = [frame1, frame2, frame3]
    combine = pd.concat(frames)
    #change to status eventually; once field is added
    #may need to deal with status = not screened here too
    combine['ReportStatus'].fillna('Repeated', inplace=True)
    return combine

def clean_repeated_records(df):    
    repeats = identify_repeats(df)
    latest_source = find_latest_source(repeats)

    newest = find_newest_repeat(repeats, latest_source)
    still_repeated = flag_still_repeated(newest)

    use1 = keep_newest(newest, still_repeated)
    use2 = keep_segments_from_same_year(newest, still_repeated)
    use3 = keep_only_admin_selected(newest, still_repeated)

    cleaned_repeats = rebuild_df(use1, use2, use3)
    return cleaned_repeats

# function to combine everything
def report_status(package_name):
    df = create_df_from_query(package_name)
    a = flag_missing_records(df)
    b = single_records(df)
    c = clean_repeated_records(df)
    
    allframes = [a, b, c]
    joined = pd.concat(allframes)
    joined = joined.sort_values(['project'], ascending = (True))

    #subset to include only necessary fields
    joined = joined[['project', 'GISID', 'CALENDAR_YEAR', 'stateroute', 'name', 'miles', 'muni1', 'muni2', 'muni3', 'ReportStatus']]

    joined.to_sql("%s_report" % package_name, engine)
    joined.to_csv("D:/dvrpc_shared/BFR_Tracking/data/paving_package/Reports/%s_report.csv" % package_name , index=False)


if __name__ == "__main__":

	engine = create_engine(db_connections.postgres_uri)

	project_folder = Path.cwd().parent
	data_folder = project_folder / "data"
	raw_packages = data_folder / "paving_package/PDFs"

	for filepath in raw_packages.rglob("*.pdf"):
		report_status(filepath.stem)