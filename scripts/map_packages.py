"""
map_packages.py
------------------

This script runs a SQL query to map package segments 
on the PennDOT RMS road network using segments numbers.
Report status and package number fields are added.
"""

from __future__ import annotations
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import env_vars as ev
from env_vars import ENGINE


county_lookup = {"B": "09", "C": "15", "D": "23", "M": "46", "P": "67"}


def parse_county_identifier(package_name):
    string = package_name
    return string.split("Summary", 1)[1][1]


def lookup_county_code(letter):
    return county_lookup[letter]


def map_package(package_name):
    code = lookup_county_code(parse_county_identifier(package_name))

    results = gpd.GeoDataFrame.from_postgis(
        fr"""
			with tblA AS(
			select "GISID" ,
				cast("	STATE_ROUTE" as varchar) ,
				"	LOC_ROAD_NAME_RMS" ,
				"	municipality1" ,
				"  municipality2" ,
				"  municipality3" ,
				"	segment_from_to" ,
				left("	segment_from_to", 4) as fsegment,
				right("	segment_from_to", 4) as tsegment,
				status 
			from filter_flags ff
		),
		tblB AS(
			select b.*, a."GISID",a.status
			from "{package_name}" b
			left outer join tblA a on
			b.sr = lpad(cast("	STATE_ROUTE" as varchar), 4, '0')
			and b.fsegment = a.fsegment
			and b.tsegment = a.tsegment
		),
		tblC as(
			SELECT
				"ST_RT_NO" as srno,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_NO" AS numeric) as seg_no,
				geometry 
			FROM penndot_rms
			WHERE "CTY_CODE" = '{code}'
		),
		tblD as(
			SELECT 
				b.*,
				c.seg_no,
				c.geometry
			FROM tblC c
			LEFT OUTER JOIN tblB b
			ON b.sr = c.srno
			)
		SELECT *
		FROM tbld 
		WHERE seg_no >= cast(fsegment as numeric)
		AND seg_no <= cast(tsegment as numeric)
		order by project_num
	""",
        con=ENGINE,
        geom_col="geometry",
    )

    results["pavingpackage"] = package_name.split("Summary", 1)[1]

    return results

def status_report(package_name):
	results = pd.read_sql(
		fr"""
		with tblA AS(
		select "GISID" ,
			cast("	STATE_ROUTE" as varchar) ,
			"	LOC_ROAD_NAME_RMS" ,
			"	municipality1" ,
			"  municipality2" ,
			"  municipality3" ,
			"	segment_from_to" ,
			left("	segment_from_to", 4) as fsegment,
			right("	segment_from_to", 4) as tsegment,
			status 
		from filter_flags ff
		)
		select b.*, a."GISID",a.status
		from "{package_name}" b
		left outer join tblA a on
		b.sr = lpad(cast("	STATE_ROUTE" as varchar), 4, '0')
		and lpad(cast(b.fsegment as varchar), 4, '0') = a.fsegment
		and lpad(cast(b.tsegment as varchar), 4, '0') = a.tsegment
		order by b.project_num ;
	""",
	con = ENGINE

	)
	return results


def map_and_write_phila(package_name):
    package = package_name.split("Summary ", 1)[1]
    gdf = map_package(package_name)
    gdf.to_file(
        fr"{ev.DATA_ROOT}/geojson/{package}_mappedreport.geojson", driver="GeoJSON"
    )
    print("To GeoJSON: Complete")


def map_with_status(package_name):
    df = map_package(package_name)
    return df


def write_results(package_name, gdf, report):
	package = package_name.split("Summary", 1)[1]
	report.to_sql(fr"{package_name}_report", ENGINE, if_exists="replace")
	report.to_csv(fr"{ev.DATA_ROOT}/paving_package/Reports/{package_name}report.csv", index = False)
	print("Report Generated")
	gdf.to_file(fr"{ev.DATA_ROOT}/shapefiles/{package}_mappedreport.shp")
	print("To shapefile: Complete")
	gdf.to_file(fr"{ev.DATA_ROOT}/geojson/{package}_mappedreport.geojson", driver = "GeoJSON")
	print("To GeoJSON: Complete")


def main():
    data_folder = Path(ev.DATA_ROOT)
    raw_packages = data_folder / "paving_package/PDFs"

    for filepath in raw_packages.rglob("*.pdf"):
        print(filepath.stem)
        report_output = status_report(filepath.stem)
        map_output = map_with_status(filepath.stem)
        write_results(filepath.stem, map_output, report_output)

    #map_and_write_phila("Location Summary P12")


if __name__ == "__main__":
    main()


