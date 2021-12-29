"""
import_oracle.py
------------------

This script pulls the latest SEPA datatable from the Oracle database.
A CSV copy of the Oracle export is saved in the /data/from_oracle with the run date.
It created a backup of the existing Oracle copy in a postgres database.
Then it inserts the latest copy under the same name.

"""

import cx_Oracle
import csv
from datetime import date
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import env_vars as ev
from env_vars import ENGINE


def main():
    today = date.today()
    print(today)

    changes = fr"{ev.DATA_ROOT}\from_oracle\db_pull_{today}.csv"

    # connect to Oracle, declare your query
    db = cx_Oracle.connect(ev.ORACLE_NAME, ev.ORACLE_PW, ev.ORACLE_HOST)
    cursor = db.cursor()
    SQL = r"SELECT * FROM SEPADATA"

    ##run cursor on db, write to csv
    cursor.execute(SQL)
    with open(changes, "w", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow([i[0] for i in cursor.description])  ##heading row
        writer.writerows(cursor.fetchall())

    df = pd.read_csv(changes)

    # create database
    if not database_exists(ENGINE.url):
        create_database(ENGINE.url)

    ENGINE.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # drop existing backup and copy previous oracle export as backup
    ENGINE.execute("DROP TABLE IF EXISTS from_oracle_backup; COMMIT;")
    ENGINE.execute("SELECT * INTO from_oracle_backup FROM from_oracle; COMMIT;")

    # write dataframe to postgis, replacing old table
    df.to_sql("from_oracle", con=ENGINE, if_exists="replace")


if __name__ == "__main__":
    main()
