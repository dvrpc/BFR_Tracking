import psycopg2 as psql
import pandas as pd
import geopandas as gpd
import os
from shapely import geometry
from sqlalchemy import create_engine
import requests

#import PennDOT's rms layer from GIS portal - RMSADMIN (Administrative Classifications of Roadway)
gdf = gpd.read_file('https://opendata.arcgis.com/datasets/a934887d51e647d295806cc2d9c02097_0.geojson')

#send to postgres db

