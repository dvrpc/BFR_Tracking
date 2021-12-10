import psycopg2 as psql
import geopandas as gpd
from shapely import geometry, wkt
from sqlalchemy import create_engine
from geoalchemy2 import Geometry, WKTElement

#update map layer to include status/package details
#overwrite segment with package segment as warrented
#change symbology to show status
