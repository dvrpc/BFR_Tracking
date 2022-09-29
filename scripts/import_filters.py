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
                        WHERE " For Initial Screening"= 1; """

q_dvrpc_screen = """UPDATE filter_flags
                    SET status = 'For DVRPC to Screen for Feasibility'
                    WHERE "	For DVRPC to Screen for Feasiblity"  = 1; """ 

q_pending_review =  """UPDATE filter_flags
                    SET status = 'Pending Review'
                    WHERE "	Pending Review" = 1; """

q_penndot_screen = """UPDATE filter_flags
                    SET status = 'For PennDOT to Screen for Feasibility'
                    WHERE " For PennDOT to Screen for Feasibility" = 1;"""

q_outreach_prio = """UPDATE filter_flags
                    SET status = 'Outreach Prioritization'
                    WHERE " Outreach Prioritization" = 1; """

q_begin_outreach = """UPDATE filter_flags
                    SET status = 'Begin Municipal Outreach'
                    WHERE "	To begin municipal outreach" = 1; """

q_letter_pending = """UPDATE filter_flags
                    SET status = 'Waiting for municipal letter'
                    WHERE "	Waiting for municipal letter"  = 1;"""

q_letter_received = """UPDATE filter_flags
                    SET status = 'Letter Received'
                    WHERE "	Municipal letter received/Needs striping plan" = 1;"""

q_completed = """UPDATE filter_flags
                SET status = 'Complete'
                WHERE "	Completed Projects" = 1; """

q_capacity_analysis = """UPDATE filter_flags
                        SET status = 'Pending Capacity Analysis'
                        WHERE " Pending Capacity Analysis" = 1; """

q_beyond_scope = """UPDATE filter_flags
                    SET status = 'Beyond Scope of Resurfacing'
                    WHERE "	Beyond scope of resurfacing" = 1; """

q_no_status = """UPDATE filter_flags
                SET status = 'Not Reviewed'
                WHERE status = 'N/A'; """


def main():
    filters = fr"{ev.DATA_ROOT}\from_oracle\filter_flags.csv"

    df = pd.read_csv(filters)
    # write dataframe to postgis, replacing old table
    df.to_sql("filter_flags", con=ENGINE, if_exists="replace")

    



if __name__ == "__main__":
    main()
