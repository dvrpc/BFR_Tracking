import psycopg2 as psql

# import pandas as pd
import geopandas as gpd

# import os
from shapely import geometry, wkt
from sqlalchemy import create_engine
from geoalchemy2 import Geometry, WKTElement

# compare package to screening records and/or projects on the shelf
"""
select 
pt.*
fo."CALENDAR_YEAR",
fo."PLANNED"
from package_test pt
left join from_oracle  fo
on cast(pt.sr AS numeric) = fo."STATE_ROUTE" 
and cast(pt.fsegment as numeric) = fo."SEGMENT_FROM" 
and cast(pt.tsegment as numeric) = fo."SEGMENT_TO"
order by routenum;
"""

# add status field to oracle table that is manually updated from a drop down list
# this status is reported along with the package once joined
