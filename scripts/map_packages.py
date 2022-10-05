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

def status_report(package_name):
	results = pd.read_sql(
		fr"""
		with tblA AS(
			select "GISID" ,
				cast("	STATE_ROUTE" as varchar) ,
				"	LOC_ROAD_NAME_RMS" ,
				"	ADMINSELECTED" ,
				"	CALENDAR_YEAR" ,
				"	municipality1" ,
				"  municipality2" ,
				"  municipality3" ,
				"	segment_from_to" ,
				left("	segment_from_to", 4) as fseg,
				right("	segment_from_to", 4) as tseg,
				status 
			from filter_flags ff
		),
		match_segments AS(	
			select b.*, a.*
			from "{package_name}" b
			left outer join tblA a on
			b.sr = lpad(cast("	STATE_ROUTE" as varchar), 4, '0')
			and (lpad(cast(b.fsegment as varchar), 4, '0') = a.fseg
			and lpad(cast(b.tsegment as varchar), 4, '0') = a.tseg)
			where "	ADMINSELECTED" = 'Y'
			order by b.project_num),
		no_match AS(
			select *
			from "{package_name}" b
			where project_num not in (select project_num from match_segments)
		),
		nomatch_join as(
			select b.*, a.*
			from no_match b
			left outer join tblA a on
			b.sr = lpad(cast(a."	STATE_ROUTE" as varchar), 4, '0')
			and ((cast(b.fsegment as numeric) >= cast(a.fseg as numeric) and cast(b.fsegment as numeric) <= cast(a.tseg as numeric))
			or (cast(b.tsegment as numeric) <= cast(a.tseg as numeric) and cast(b.tsegment as numeric) >= cast(a.fseg as numeric)))
			and (upper(b.muni1) = a."	municipality1" or upper(b.muni1) = a."  municipality2" or upper(b.muni1) = a."  municipality3")
			where "	ADMINSELECTED" = 'Y'
			order by b.project_num
			),
		in_db_union as(
			select *
			from match_segments
			union all
			select *
			from nomatch_join
			order by project_num
		),
		not_in_db as(
			select *
			from "{package_name}" b
			where project_num not in (select project_num from in_db_union)
		),
		blank_join as(
			select b.*, a.*
			from not_in_db b
			left join tblA a on
			b.sr = lpad(cast("	STATE_ROUTE" as varchar), 4, '0')
			and (lpad(cast(b.fsegment as varchar), 4, '0') = a.fseg
			and lpad(cast(b.tsegment as varchar), 4, '0') = a.tseg)
			order by project_num
			)
		select *
		from in_db_union
		union all
		select *
		from blank_join
		order by project_num
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


def map_package(package_name):
	#map left set of fseg/tseg
	code = lookup_county_code(parse_county_identifier(package_name))
	results = gpd.GeoDataFrame.from_postgis(
		fr"""with tblC as(
			SELECT
				"ST_RT_NO" as srno,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_NO" AS numeric) as seg_no,
				geometry 
			FROM penndot_rms
			WHERE "CTY_CODE" = '{code}'
		)
		SELECT 
			a.*,
			c.seg_no,
			c.geometry
		FROM tblC c
		LEFT OUTER JOIN "{package_name}_report" a
		ON a.sr = c.srno
		WHERE seg_no >= cast(fsegment as numeric)
		AND seg_no <= cast(tsegment as numeric)
		order by project_num""",
        con=ENGINE,
        geom_col="geometry",
    )

	return results

def map_relevant_segments(package_name):
	#q to joing to map right set of fseg/tseg
	code = lookup_county_code(parse_county_identifier(package_name))
	results = gpd.GeoDataFrame.from_postgis(
		fr"""with tblC as(
			SELECT
				"ST_RT_NO" as srno,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_NO" AS numeric) as seg_no,
				geometry 
			FROM penndot_rms
			WHERE "CTY_CODE" = '{code}'
		)
		SELECT 
			a.*,
			c.seg_no,
			c.geometry
		FROM tblC c
		LEFT OUTER JOIN "{package_name}_report" a
		ON a.sr = c.srno
		WHERE seg_no >= cast(fseg as numeric)
		AND seg_no <= cast(tseg as numeric)
		order by project_num""",
		        con=ENGINE,
        geom_col="geometry",
    )

	return results



def write_and_map_results(package_name, report):
	package = package_name.split("Summary", 1)[1]
	report.to_sql(fr"{package_name}_report", ENGINE, if_exists="replace")
	report.to_csv(fr"{ev.DATA_ROOT}/paving_package/Reports/{package_name}report.csv", index = False)
	print("Report Generated")

	gdf_pkg = map_package(package_name)
	gdf_seg = map_relevant_segments(package_name)

	gdf_pkg.to_file(fr"{ev.DATA_ROOT}/shapefiles/{package}_mappedpkg.shp")
	gdf_seg.to_file(fr"{ev.DATA_ROOT}/shapefiles/{package}_mappedreport.shp")
	print("To shapefiles: Complete")
	gdf_pkg.to_file(fr"{ev.DATA_ROOT}/geojson/{package}_mappedpkg.geojson", driver = "GeoJSON")
	gdf_seg.to_file(fr"{ev.DATA_ROOT}/geojson/{package}_mappedreport.geojson", driver = "GeoJSON")
	print("To GeoJSONs: Complete")


def main():
    data_folder = Path(ev.DATA_ROOT)
    raw_packages = data_folder / "paving_package/PDFs"

    for filepath in raw_packages.rglob("*.pdf"):
        print(filepath.stem)
        report_output = status_report(filepath.stem)
        write_and_map_results(filepath.stem, report_output)

    #map_and_write_phila("Location Summary P12")


if __name__ == "__main__":
    main()


