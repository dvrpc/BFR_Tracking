import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

#read export from oracle to dataframe
fp = "D:\dvrpc_shared\BFR_Tracking\BIKELANETRACKING_SEPADATA_export_111821.xlsx"
df = pd.read_excel(fp)

#create database
engine = create_engine("postgresql://postgres:root@localhost:5432/bfr_tracking")
if not database_exists(engine.url):
    create_database(engine.url)

engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
#engine.execute("COMMIT;")

#write dataframe to postgis
df.to_sql("from_oracle", con=engine, if_exists='replace')