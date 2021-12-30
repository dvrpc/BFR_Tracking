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

from sqlalchemy.engine.base import TwoPhaseTransaction
import env_vars as ev
from env_vars import ENGINE


county_lookup = {"B": "09", "C": "15", "D": "23", "M": "46", "P": "51"}


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
		select 
			project_num,
			sr, 
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
			"ST_RT_NO" as srno ,
			CAST("CTY_CODE" AS numeric) as co_no,
			CAST("SEG_BGN" AS numeric) as seg_no,
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

    results = gpd.GeoDataFrame.from_postgis(
        fr"""
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
			from "{package_name}" lsc
			),
		tblB AS(
			SELECT
				"ST_RT_NO" as srno ,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_BGN" AS numeric) as seg_no,
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
        geom_col="geometry",
    )

    return results


def flag_not_evaluated_segments(package_name):
    code = lookup_county_code(parse_county_identifier(package_name))

    results = gpd.GeoDataFrame.from_postgis(
        fr"""
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
			from "{package_name}" lsc
			),
		tblB AS(
			SELECT
				"ST_RT_NO" as srno ,
				CAST("CTY_CODE" AS numeric) as co_no,
				CAST("SEG_BGN" AS numeric) as seg_no,
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
        geom_col="geometry",
    )

    return results


def compile_status(df_status, df_non):
    test
    return s


def map_with_status(df_status, df_geom):
    test
    return x


def write_results(gdf, package_name):
    package = package_name.split("Summary ", 1)[1]
    # output report CSV
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
        write_results(map_package(filepath.stem), filepath.stem)


if __name__ == "__main__":
    main()
