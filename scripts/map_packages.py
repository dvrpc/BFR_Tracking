"""
map_packages.py
------------------

This script runs a SQL query to map package segments 
on the PennDOT RMS road network using segments numbers.
Report status and package number fields are added.

TO DO
- update GISID fiels with STATUS field once available

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


def join_status(package_name):
	code = lookup_county_code(parse_county_identifier(package_name))

	results = pd.read_sql(
		fr"""with tblA AS(
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
			and
			b.fsegment = a.fsegment
			and
			b.tsegment = a.tsegment
			""",
			con = ENGINE


	)
	return results

def map_package(package_name):
    code = lookup_county_code(parse_county_identifier(package_name))

    results = gpd.GeoDataFrame.from_postgis(
        fr"""
	with tblA AS(
		select 
			project_num,
			CAST(sr AS text) as sr, 
			name,
			muni1,
			muni2,
			muni3,
			cast(fsegment as numeric) as sf,
			cast(tsegment as numeric) as st
		from "{package_name}" lsc
		),
	tblB AS(
		SELECT
			"ST_RT_NO" as srno,
			CAST("CTY_CODE" AS numeric) as co_no,
			CAST("SEG_NO" AS numeric) as seg_no,
			geometry 
		FROM penndot_rms
		WHERE "CTY_CODE" = '{code}'
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
		order by project_num
	)
	select 
		ms."GISID",	
		d.project_num,
		d.sr,
		d.name,
		d.muni1,
		d.muni2,
		d.muni3,
		d.geometry
	from tblD d
	left join mapped_segments ms
	on d.geometry = ms.geometry
	""",
        con=ENGINE,
        geom_col="geometry",
    )

    results["pavingpackage"] = package_name.split("Summary", 1)[1]

    return results


def summarize_evaluted_segments(package_name):
    code = lookup_county_code(parse_county_identifier(package_name))

    results = pd.read_sql(
        fr"""
		with tblA AS(
			select 
				project_num,
				CAST(sr AS text) as sr, 
				name,
				muni1,
				muni2,
				muni3,
				cast(fsegment as numeric) as sf,
				cast(tsegment as numeric) as st
			from "{package_name}" lsc
			),
		tblB AS(
			SELECT
				"ST_RT_NO" as srno,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_NO" AS numeric) as seg_no,
				geometry 
			FROM penndot_rms
			WHERE "CTY_CODE" = '{code}'
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
			order by project_num
		),
		tblE AS( 
		select 
			ms."GISID",	
			d.project_num,
			d.sr,
			d.name,
			d.muni1,
			d.muni2,
			d.muni3,
			d.geometry
		from tblD d
		left join mapped_segments ms
		on d.geometry = ms.geometry
		)
		select
			project_num,
			sr,
			name,
			string_agg(distinct cast("GISID" as text), ', ') as gisids
		from tblE
		group by project_num, sr, name
			""",
        con=ENGINE,
    )

    return results


def flag_not_evaluated_segments(package_name):
    code = lookup_county_code(parse_county_identifier(package_name))

    results = pd.read_sql(
        fr"""
		with tblA AS(
			select 
				project_num,
				CAST(sr AS text) as sr, 
				name,
				muni1,
				muni2,
				muni3,
				cast(fsegment as numeric) as sf,
				cast(tsegment as numeric) as st
			from "{package_name}" lsc
			),
		tblB AS(
			SELECT
				"ST_RT_NO" as srno,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_NO" AS numeric) as seg_no,
				geometry 
			FROM penndot_rms
			WHERE "CTY_CODE" = '{code}'
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
			order by project_num
		),
		tblE AS( 
		select 
			ms."GISID",	
			d.project_num,
			d.sr,
			d.name,
			d.muni1,
			d.muni2,
			d.muni3,
			d.geometry
		from tblD d
		left join mapped_segments ms
		on d.geometry = ms.geometry
		)
		select
			project_num,
			sr,
			name,
			COUNT(*)
		from tblE
		where "GISID" is null 
		group by project_num, sr, name
		""",
        con=ENGINE,
    )

    return results


def map_and_write_phila(package_name):
    package = package_name.split("Summary ", 1)[1]
    gdf = map_package(package_name)
    gdf.to_file(
        fr"{ev.DATA_ROOT}/geojson/{package}_mappedreport.geojson", driver="GeoJSON"
    )
    print("To GeoJSON: Complete")


def compile_status_report(package_name):
    evaluated = pd.DataFrame(summarize_evaluted_segments(package_name))
    has_null = pd.DataFrame(flag_not_evaluated_segments(package_name))

    # subset of projects that have no segments that do not overlap the 5-year plan mapped segments
    fully_evaluated = evaluated[-evaluated.project_num.isin(has_null.project_num)]
    # none of the project segments overlap the 5 year plan
    not_evaluated = evaluated[evaluated.gisids.isnull()]
    # projects where some of the segment overlaps the 5 year plan
    a = evaluated[evaluated.project_num.isin(has_null.project_num)]
    partially_evaluated = a[-a.project_num.isin(not_evaluated.project_num)]

    fully_evaluated["status"] = "Fully Evaluated"
    not_evaluated["status"] = "Not Evaluated"
    partially_evaluated["status"] = "Partially Evaluated"
    union = pd.concat([fully_evaluated, not_evaluated, partially_evaluated])
    # union.set_index('project_num', inplace=True)
    output = union.sort_values("project_num")
    return output


def map_with_status(package_name, report):
    df = map_package(package_name)
    to_map = df.join(report["status"], on="project_num")
    to_map["status"].fillna("Not Evaluated", inplace=True)
    return to_map


def write_results(package_name, gdf, report):
    package = package_name.split("Summary ", 1)[1]

    report.to_sql(fr"{package_name}_report", ENGINE, if_exists="replace")

    report.to_csv(
        fr"{ev.DATA_ROOT}/paving_package/Reports/{package_name}_report.csv", index=False
    )
    print("Report Generated")
    gdf.to_file(fr"{ev.DATA_ROOT}/shapefiles/{package}_mappedreport.shp")
    print("To shapefile: Complete")
    gdf.to_file(
        fr"{ev.DATA_ROOT}/geojson/{package}_mappedreport.geojson",
        driver="GeoJSON",
    )
    print("To GeoJSON: Complete")


def main():
    data_folder = Path(ev.DATA_ROOT)
    raw_packages = data_folder / "paving_package/PDFs"

    for filepath in raw_packages.rglob("*.pdf"):
        print(filepath.stem)
        report_output = compile_status_report(filepath.stem)
        map_output = map_with_status(filepath.stem, report_output)
        write_results(filepath.stem, map_output, report_output)

    map_and_write_phila("Location Summary P12")


if __name__ == "__main__":
    main()
