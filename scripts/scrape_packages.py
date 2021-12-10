"""
scrape_packages.py
------------------

This script loops over every PDF within a given folder.
For each PDF, it extracts tabular data from every page,
parses attributes into new columns, and adds new rows
for any PDF rows that contain two segments instead of one.
"""

from __future__ import annotations
from pathlib import Path
import tabula
import pandas as pd
from PyPDF2 import PdfFileReader
from sqlalchemy import create_engine

def remove_returns_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function removes all occurances of '\r' in every column
    of the input dataframe.
    """
    for column in df.columns:
        df[column] = df[column].str.replace("\r", " ")
    return df


def drop_total_row_if_exists(df: pd.DataFrame) -> pd.DataFrame:
    """
    The final page of the PDF set has a 'Total' row.
    This function finds the index of that row if it exists,
    and then drops that row.
    """
    for idx, row in df.iterrows():
        if type(row["project_num"]) == str:
            if row["project_num"].lower() == "total":
                df.drop(idx, inplace=True)

    return df


def sort_df_by_project_id(df: pd.DataFrame, sort_column: str = "project_num") -> pd.DataFrame:
    """
    After adding new rows, we want to be able to sort the resulting table
    before writing it to file.
    """
    df[sort_column] = df[sort_column].astype(float)

    df.sort_values(sort_column, inplace=True)

    return df


def get_number_of_pages_in_pdf(filepath: Path | str) -> int:
    """
    Open a PDF file and return the number of pages within
    """
    with open(filepath, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        number_of_pages = pdf_reader.numPages

    return number_of_pages


def read_single_page_from_pdf(
    filepath: Path | str,
    page_number: int,
    column_names: list = ["project_num", "SR_name", "from", "to", "scope", "miles", "muni", "adt"],
) -> pd.DataFrame:
    """
    - Read a specific page of a PDF
    - `tabula` returns a list containing dataframes. Use the first item
       since we're reading one page at a time.
    - Drop the first two rows of the resulting dataframe before returning
    """
    df = tabula.read_pdf(filepath, pages=page_number)[0]
    df.columns = column_names

    # drop rows 1 & 2 and column 1 (with assigned row numbers)
    # df = df.iloc[2:, :]
    rows_to_drop = [0, 1]
    df.drop(rows_to_drop, inplace=True)

    # drop the 'total' row if it's in the dataframe
    df = drop_total_row_if_exists(df)

    return df


def extract_data_from_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Many of the values are comma-, slash-, or otherwise delimited.

    This function takes the raw dataframe, extracts data into new
    columns as needed, and returns the dataframe.
    """
    # # parse out columns for easier comparison with data tables
    df["sr"] = df["SR_name"].str.split("\r", n=1, expand=True)[0]
    df["sr"] = df["sr"].str[3:]
    df["name"] = df["SR_name"].str.split("\r", n=1, expand=True)[1]

    # the municipality list is of variable length, depending on file.
    # this code ensures there's 3 muni columns, regardless of source data
    muni_list = df["muni"].str.split(",", expand=True)
    for col_idx in muni_list.columns:
        df[f"muni{col_idx + 1}"] = muni_list[col_idx]

    missing_columns = set(muni_list.columns).symmetric_difference(set(range(3)))
    for col_idx in missing_columns:
        df[f"muni{col_idx + 1}"] = ""

    # parse out segment/offset from 'from' and 'to' columns for mapping
    df[["fsegment", "from"]] = df["from"].str.split("\r", n=1, expand=True)
    df[["fsegment", "foffset"]] = df["fsegment"].str.split("/", n=1, expand=True)
    df[["tsegment", "to"]] = df["to"].str.split("\r", n=1, expand=True)
    df[["tsegment", "toffset"]] = df["tsegment"].str.split("/", n=1, expand=True)

    return df


def row_should_become_two(row: pd.Series) -> bool:
    """
    If the first digit in the `from` column is an integer,
    the row needs to be split into two.
    """
    return str(row["from"])[0].isdigit()


def parse_single_page(filepath: Path, page_number: int) -> pd.DataFrame:
    """
    Extract data from a single page of a PDF
    - Identify rows that need to be split apart
    - For any of these rows, modify the existing row and add a new one
    """
    df = read_single_page_from_pdf(filepath, page_number=page_number)

    df = extract_data_from_columns(df)

    for idx, row in df.iterrows():
        if row_should_become_two(row):
            # extract values from specific cells in the row
            f1, f2 = row["from"].split("\r", 1)
            fs, fo = f1.split("/", 1)
            t1, t2 = row["to"].split("\r", 1)
            ts, to = t1.split("/", 1)
            m1, m2 = row["miles"].split("\r", 1)

            # update existing row
            row["from"] = f2
            row["to"] = t2
            row["miles"] = m1

            # add new row to dataframe
            new_row = dict(row.copy())
            new_row["miles"] = m2
            new_row["fsegment"] = fs
            new_row["foffset"] = fo
            new_row["tsegment"] = ts
            new_row["toffset"] = to

            df = df.append(new_row, ignore_index=True)

    return df


def parse_single_pdf(filepath: Path, output_folder: Path) -> pd.DataFrame:
    """
    Run all of the business logic for a single PDF file which has multiple pages.
    - After repeating this for each page, merge all results into a singluar CSV output
    """
    print(f"Parsing: {filepath.stem}")

    num_pgs = get_number_of_pages_in_pdf(filepath)

    # append records from each page to dataframe
    frames = []
    for i in range(1, num_pgs + 1):

        df = parse_single_page(filepath, page_number=i)

        frames.append(df)

    allpgs = pd.concat(frames, ignore_index=True)

    cleaned_df = remove_returns_from_dataframe(allpgs)
    cleaned_df = sort_df_by_project_id(cleaned_df)

    output_filepath = output_folder / f"{filepath.stem}.csv"

    cleaned_df.to_csv(output_filepath, index=False)
    engine = create_engine('postgresql://postgres:root@localhost:5432/bfr_tracking')
    cleaned_df.to_sql(f"{filepath.stem}", engine)


if __name__ == "__main__":
    data_folder = Path("./data")
    paving_package = data_folder / "paving_package"
    output_folder = paving_package / "CSVs"

    for filepath in paving_package.rglob("*.pdf"):
        parse_single_pdf(filepath, output_folder)
