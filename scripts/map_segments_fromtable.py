"""
map_segments_fromtable.py
------------------

This script maps the entire oracle database table 
using the PennDOT RMS later from PennDOT's GIS portal.
Once generated, this does not need to be run for 
every package comparison. However, it should be 
updated regularly.

"""


import geopandas as gpd
from geoalchemy2 import WKTElement
import env_vars as ev
from env_vars import ENGINE

# import PennDOT's rms layer from GIS portal - RMSSEG (State Roads)
gdf = gpd.read_file(
    "https://opendata.arcgis.com/datasets/d9a2a5df74cf4726980e5e276d51fe8d_0.geojson"
)

# remove null geometries
gdf = gdf[gdf.geometry.notnull()]
# remove records outside of district 6
gdf = gdf.loc[gdf["DISTRICT_NO"] == "06"]

# transform projection from 4326 to 26918
gdf = gdf.to_crs(epsg=26918)

# create geom column for postgis import
gdf["geom"] = gdf["geometry"].apply(lambda x: WKTElement(x.wkt, srid=26918))

# write geodataframe to postgis
gdf.to_postgis("penndot_rms", con=ENGINE, if_exists="replace")

# join to bfr segment table
results = gpd.GeoDataFrame.from_postgis(
    """
	WITH tblA AS(
	SELECT 
		"GISID",
        "CALENDAR_YEAR" ,
		to_char(CAST("STATE_ROUTE" AS numeric), 'fm0000') AS sr,
		"LOC_ROAD_NAME_RMS",
		"INTERSECTION_FROM" ,
		CAST("SEGMENT_FROM" AS numeric) AS sf,
		"OFFSET_FROM" ,
		"INTERSECTION_TO" ,
		CAST("SEGMENT_TO" AS numeric) AS st,
		"OFFSET_TO" ,
		"MUNICIPALITY_NAME1" ,
		"MUNICIPALITY_NAME2" ,
		"MUNICIPALITY_NAME3" ,
		"PLANNED" ,
		"COUNTY" ,
		"CNT_CODE" as co_no
	FROM from_oracle
	),

	tblB AS(
		SELECT
			"ST_RT_NO" as srno ,
			CAST("CTY_CODE" AS numeric) as co_no,
			CAST("SEG_BGN" AS numeric) as seg_no,
			geometry 
		FROM penndot_rms
		),

	tblC AS(
		SELECT 
			a.*,
			b.seg_no,
			b.geometry
		FROM tblB b
		LEFT OUTER JOIN tblA a
		ON a.sr = b.srno
		AND a.co_no = b.co_no)

	SELECT *
	FROM tblC 
	WHERE seg_no >= sf
	AND seg_no <= st
	AND "CALENDAR_YEAR" IS NOT NULL;
""",
    con=ENGINE,
    geom_col="geometry",
)

# output spatial file (postgis, shp, and geojson)
results.to_postgis("mapped_segments", con=ENGINE, if_exists="replace")
print("To database: Complete")
results.to_file(fr"{ev.DATA_ROOT}/mapped_segments_shapefile/mapped_segments.shp")
print("To shapefile: Complete")
results.to_file(
    fr"{ev.DATA_ROOT}/mapped_segments_geojson/mapped_segments.geojson",
    driver="GeoJSON",
)
print("To GeoJSON: Complete")
