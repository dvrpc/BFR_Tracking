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
'''
# Use GeoAlchemy's WKTElement to create a geom with SRID
def create_wkt_element(geom):
    return WKTElement(geom.wkt, srid = 26918)

gdf['geom'] = gdf['geometry'].apply(create_wkt_element)

# Use 'dtype' to specify column's type
# For the geom column, we will use GeoAlchemy's type 'Geometry'
gdf.to_sql(table_name, engine, if_exists='append', index=False, 
                         dtype={'geom': Geometry('POINT', srid= 26918)})
'''
#create geom column for postgis import
# gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=26918))
# gdf.drop("geometry", 1, inplace=True)
# gdf.set_geometry('geom')
gdf['geom'] = gdf['geom'].apply(wkt.loads)

#write geodataframe to postgis
db_connection_url = "postgresql://postgres:root@localhost:5432/bfr_tracking"
engine = create_engine(db_connection_url)
gdf.to_postgis("penndot_rms", con=engine, if_exists='replace')

#join to bfr segment table
'''

WITH tblA AS(
	SELECT 
		year,
		to_char(CAST(stateroute AS numeric), 'fm0000') AS sr,
		loc,
		intersectionfrom,
		CAST(segfrom AS numeric) AS sf,
		offsetfrom,
		intersectionto,
		CAST(segto AS numeric) AS st,
		offsetto,
		muni1,
		muni2,
		muni3,
		plannedmiles,
		county,
		county_code,
		shortcode,
		longcode,
		changecode
	FROM "FiveYr_Plan_19-23"
	),

tblB AS(
	SELECT
		st_rt_no,
		cty_code,
		CAST(seg_no AS numeric),
		street_nam,
		bgn_desc,
		end_desc,
		st_transform(geom, 26918) AS geom
	FROM penndot_rms_segments_101518
	),

tblC AS(
	SELECT 
		b.*,
		a.*
	FROM tblB b
	LEFT OUTER JOIN tblA a
	ON a.sr = b.st_rt_no
	AND a.county_code = b.cty_code)

SELECT *
FROM tblC 
WHERE seg_no >= sf
AND seg_no <= st
AND year IS NOT NULL
'''
#output spatial file (table or shp or geojson?)

