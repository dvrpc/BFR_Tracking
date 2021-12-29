"""
map_packages.py
------------------

This script runs a SQL query to map package segments 
on the PennDOT RMS road network using segments numbers.
Report status and package number fields are added.

"""

from __future__ import annotations
import geopandas as gpd
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from pathlib import Path
import env_vars as ev


county_lookup = {"B": 9, "C": 15, "D": 23, "M": 46, "P": 51}


def parse_county_identifier(package_name):
    string = package_name
    return string.split("Summary", 1)[1][1]


def lookup_county_code(letter):
    return county_lookup[letter]


def map_package(package_name):
    report_table = package_name + "_report"
    code = lookup_county_code(parse_county_identifier(package_name))

    results = gpd.GeoDataFrame.from_postgis(
        """
	with tblA AS(
		select 
			project_num,
			sr, 
			name,
			muni1,
			muni2,
			muni3,
			cast(fsegment as numeric) as sf,
			cast(tsegment as numeric) as st
		from "%s" lsc
		),
	tblB AS(
		SELECT
			"ST_RT_NO" as srno ,
			CAST("CTY_CODE" AS numeric) as co_no,
			CAST("SEG_BGN" AS numeric) as seg_no,
			geometry 
		FROM penndot_rms
		WHERE "CTY_CODE" = '%s'
		),
	tblC AS(
		SELECT 
			a.*,
			b.seg_no,
			b.geometry
		FROM tblB b
		LEFT OUTER JOIN tblA a
		ON a.sr = b.srno
		),
	tblD AS(
		SELECT *
		FROM tblC 
		WHERE seg_no >= sf
		AND seg_no <= st
		)
	select 
		d.*,
		ls."ReportStatus" 
	from tblD d
	inner join "%s" ls 
	on d.project_num = ls.project;
	"""
        % (package_name, code, report_table),
        con=engine,
        geom_col="geometry",
    )

    results["pavingpackage"] = package_name.split("Summary", 1)[1]

    return results


def write_results(gdf, package_name):
    package = package_name.split("Summary", 1)[1]
    # gdf.to_postgis("%s_mappedreport" % package, con=engine, if_exists='replace')
    # print("To database: Complete")
    gdf.to_file(
        "D:/dvrpc_shared/BFR_Tracking/data/shapefiles/%s_mappedreport.shp" % package
    )
    print("To shapefile: Complete")
    gdf.to_file(
        "D:/dvrpc_shared/BFR_Tracking/data/geojson/%s_mappedreport" % package,
        driver="GeoJSON",
    )
    print("To GeoJSON: Complete")


def main():
    project_folder = Path.cwd().parent
    data_folder = project_folder / "data"
    raw_packages = data_folder / "paving_package/PDFs"

    for filepath in raw_packages.rglob("*.pdf"):
        print(filepath.stem)
        write_results(map_package(filepath.stem), filepath.stem)


if __name__ == "__main__":
    engine = create_engine(ev.POSTGRES_URL)
    main()
