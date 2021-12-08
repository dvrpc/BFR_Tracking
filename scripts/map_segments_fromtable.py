###
# To Do:
# add road name to shapefile output for ease of use 

import psycopg2 as psql
#import pandas as pd
import geopandas as gpd
#import os
from shapely import geometry, wkt
from sqlalchemy import create_engine
from geoalchemy2 import Geometry, WKTElement


#import PennDOT's rms layer from GIS portal - RMSADMIN (Administrative Classifications of Roadway)
gdf = gpd.read_file('https://opendata.arcgis.com/datasets/a934887d51e647d295806cc2d9c02097_0.geojson')

#remove null geometries
gdf = gdf[gdf.geometry.notnull()]
#remove records outside of district 6
gdf = gdf.loc[gdf['DISTRICT_NO'] == '06']

#transform projection from 4326 to 26918
gdf = gdf.to_crs(epsg=26918)

#create geom column for postgis import
gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=26918))

#write geodataframe to postgis
db_connection_url = "postgresql://postgres:root@localhost:5432/bfr_tracking"
engine = create_engine(db_connection_url)
gdf.to_postgis("penndot_rms", con=engine, if_exists='replace')

#join to bfr segment table
results = gpd.GeoDataFrame.from_postgis("""
	WITH tblA AS(
	SELECT 
		"GISID",
        "CALENDAR_YEAR" ,
		to_char(CAST("STATE_ROUTE" AS numeric), 'fm0000') AS sr,
		"LOC_ROAD_NAME_RMS" 
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
""", con= engine, geom_col= "geometry")

#output spatial file (postgis and shp)
results.to_postgis("mapped_segments", con=engine, if_exists='replace')
print("To database: Complete")
results.to_file("D:/dvrpc_shared/BFR_Tracking/mapped_segments.shp")
print("To shapefile: Complete")
