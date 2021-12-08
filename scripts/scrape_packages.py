####
# TO DO:
# need a way to flag and fix multipiece segments
# delete bottom row - totals
from __future__ import annotations
from pathlib import Path
import tabula
import os
import pandas as pd
from PyPDF2 import PdfFileReader


def get_number_of_pages_in_pdf(filepath: Path | str) -> int:
    """
    Open a PDF file and return the number of pages within
    """
    with open(filepath, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        return pdf_reader.numPages


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

    return df


def extract_data_from_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Many of the values are comma-, slash-, or otherwise delimited.

    This function takes the raw dataframe, extracts data into new
    columns as needed, and returns the dataframe.
    """
    # # parse out columns for easier comparison with data tables
    # df["sr"] = df["SR_name"].str.split("\r", n=1, expand=True)[0]
    # df["sr"] = df["sr"].str[3:]
    # df["name"] = df["SR_name"].str.split("\r", n=1, expand=True)[1]
    # df["muni1"] = df["muni"].str.split(",", expand=True)[0]
    # df["muni2"] = df["muni"].str.split(",", expand=True)[1]
    # df["muni3"] = df["muni"].str.split(",", expand=True)[2]

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


def parse_single_pdf(filepath: Path) -> pd.DataFrame:
    """
    Run all of the business logic for a single PDF file.

    - Get the number of pages, and loop through each one
    - Identify rows that need to be split apart
    - For any of these rows, modify the existing row and add a new one

    - After repeating this for each page, merge all results into a singluar CSV output
    """
    print(f"Parsing: {filepath.stem}")

    num_pgs = get_number_of_pages_in_pdf(filepath)

    # append records from each page to dataframe
    frames = []
    for i in range(1, num_pgs + 1):
        df = read_single_page_from_pdf(filepath, page_number=i)

        df = extract_data_from_columns(df)

        output_filepath = filepath.parent / f"{filepath.stem}-{i}.json"
        df.to_json(output_filepath)

        for idx, row in df.iterrows():
            if row_should_become_two(row):
                print("\t Splitting into two:")
                print(row)

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

        frames.append(df)

    allpgs = pd.concat(frames, ignore_index=True)

    output_filepath = filepath.parent / f"{filepath.stem}.json"

    allpgs.to_json(output_filepath)


if __name__ == "__main__":
    pdf_folderpath = "./data/paving_package"

    for filepath in Path(pdf_folderpath).rglob("*.pdf"):
        parse_single_pdf(filepath)
