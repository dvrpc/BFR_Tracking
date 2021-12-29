import cx_Oracle
import csv
from datetime import date
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import db_connections

today = date.today()
print(today)

changes = r"D:\dvrpc_shared\BFR_Tracking\data\from_oracle\db_pull_%s.csv" % today

#connect to Oracle, declare your query
db = cx_Oracle.connect(db_connections.oracle_name, db_connections.oracle_pw, db_connections.oracle_host)
cursor = db.cursor()
SQL=r"SELECT * FROM SEPADATA"

##run cursor on db, write to csv
cursor.execute(SQL)
with open(changes, 'w', encoding='utf-8') as fout:
    writer = csv.writer(fout)
    writer.writerow([ i[0] for i in cursor.description ]) ##heading row
    writer.writerows(cursor.fetchall())

df = pd.read_csv(changes)

#create database
engine = create_engine(db_connections.postgres_uri)
if not database_exists(engine.url):
    create_database(engine.url)

engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

#drop existing backup and copy previous oracle export as backup
engine.execute("DROP TABLE IF EXISTS from_oracle_backup; COMMIT;")
engine.execute("SELECT * INTO from_oracle_backup FROM from_oracle; COMMIT;")

#write dataframe to postgis, replacing old table
df.to_sql("from_oracle", con=engine, if_exists='replace')