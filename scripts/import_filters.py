"""
import_filters.py
------------------

This script reads the data export (CSV) from the web interface of the Oracle database.
It contains flags identifiying the current filter from each record which is used to
gernerate a status attribute.

"""

import csv
from datetime import date
import pandas as pd
import env_vars as ev
from env_vars import ENGINE

q_create_field = """ALTER TABLE filter_flags
                    ADD COLUMN status varchar;"""

q_initial_screening = """UPDATE filter_flags
                        SET status = 'Initial Screening'
                        WHERE "For Initial Screening"= 1; """

q_dvrpc_screen = """UPDATE filter_flags
                    SET status = 'For DVRPC to Screen for Feasibility'
                    WHERE "For DVRPC to Screen for Feasiblity"  = 1; """ 

q_penndot_screen = """UPDATE filter_flags
                    SET status = 'Pending Review'
                    WHERE "Pending Review" = 1; """

q_outreach_prio = 

q_begin_outreach = 

q_letter_pending = 

q_letter_received = 

q_completed = 

q_capacity_analysis = 

q_beyond_scope =


def main():
    filters = fr"{ev.DATA_ROOT}\from_oracle\filter_flags.csv"

    df = pd.read_csv(filters)
    # write dataframe to postgis, replacing old table
    df.to_sql("filter_flags", con=ENGINE, if_exists="replace")



if __name__ == "__main__":
    main()
