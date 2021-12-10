### TO DO
# - if null from join, not on latest 5 year plan
# - if future year, not screened
# - if screened, what is status -> Need new status field


import psycopg2 as psql

# import pandas as pd
import geopandas as gpd

# import os
from shapely import geometry, wkt
from sqlalchemy import create_engine
from geoalchemy2 import Geometry, WKTElement


engine = create_engine('postgresql://postgres:root@localhost:5432/bfr_tracking')

# compare package to screening records and/or projects on the shelf
"""
with tblA as (
select 
lsc.project_num ,
fo."GISID" ,
fo."CALENDAR_YEAR",
fo."ADMINSELECTED",
fo."SOURCE" ,
fo."CHANGECODE" ,
lsc.sr,
lsc."name" ,
lsc."from" ,
lsc. "to",
lsc.miles ,
fo."PLANNED" as db_miles,
lsc.muni1 ,
lsc.muni2,
lsc.muni3
from "Location Summary C12" lsc 
left join from_oracle  fo
on cast(lsc.sr AS numeric) = fo."STATE_ROUTE" 
and cast(lsc.fsegment as numeric) = fo."SEGMENT_FROM" 
and cast(lsc.tsegment as numeric) = fo."SEGMENT_TO"
--where fo."SOURCE" = '5-year plan 2020-2024'
order by lsc.project_num
),
tblB as (
select
	project_num,
	count(project_num) as count
from tblA
group by project_num 
),
tblC as (
select
	tblA.*,
	tblB.count
from tblA
inner join tblB
on tblA.project_num = tblB.project_num
),
not_repeated AS(
select *
from tblC
where count = 1
),
repeated AS(
select *
from tblC
where count > 1
and "SOURCE" <> '5-year plan 2019-2023'
)
select *
from not_repeated
union all
select *
from repeated
order by project_num 
"""

# add status field to oracle table that is manually updated from a drop down list
# this status is reported along with the package once joined
