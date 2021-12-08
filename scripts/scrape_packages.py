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

pdf_folderpath = "./data/paving_package"

# function to insert row into DF
def Insert_row(row_number, df, row_values):
    df1 = df[0:row_number]
    df2 = df[row_number:]
    # for v in range(0, len(row_values)):
    df1.loc[row_number] = row_values
    df_result = pd.concat([df1, df2], ignore_index=True)
    # df_result.reset_index(drop = True)
    return df_result


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


def split_text_from_one_column_to_many(
    df: pd.DataFrame, source_column: str, dest_columns: list, splitter_text: str
) -> pd.DataFrame:
    """
    Some columns hold data that needs to be exploded into multiple columns
    This function uses a `splitter_text` pattern to move this data from
    one column into multiple
    """
    df[dest_columns] = df[source_column].str.split(splitter_text, n=1, expand=True)
    return df


def row_should_become_two(row: pd.Series) -> bool:
    """
    If the first digit in the `from` column is an integer,
    the row needs to be split into two. 
    """
    return str(row["from"])[0].isdigit()


if __name__ == "__main__":
    for filepath in Path(pdf_folderpath).rglob("*.pdf"):

        num_pgs = get_number_of_pages_in_pdf(filepath)

        # append records from each page to dataframe
        frames = []
        for i in range(1, num_pgs + 1):
            df = read_single_page_from_pdf(filepath, page_number=i)

            # parse out segment/offset from 'from' and 'to' columns for mapping
            df = split_text_from_one_column_to_many(df, "from", ["fsegment", "from"], "\r")
            df = split_text_from_one_column_to_many(df, "fsegment", ["fsegment", "foffset"], "/")
            df = split_text_from_one_column_to_many(df, "to", ["tsegment", "to"], "\r")
            df = split_text_from_one_column_to_many(df, "tsegment", ["tsegment", "toffset"], "/")

            for idx, row in df.iterrows():
                if row_should_become_two(row):
                    print("This row needs to be split into two:")
                    print(row)

                    replacement_row = list(row)

            # split out rows with multiple segment/offsets into replacement and new rows
            for k in range(0, len(df["from"])):
                p = str(df.iloc[k, 0])  # project_num
                s = str(df.iloc[k, 1])  # sr_name
                f = str(df.iloc[k, 2])  # from
                t = str(df.iloc[k, 3])  # to
                sc = str(df.iloc[k, 4])  # scope
                m = str(df.iloc[k, 5])  # miles
                mu = str(df.iloc[k, 6])  # muni
                a = str(df.iloc[k, 7])  # adt
                fseg = str(df.iloc[k, 8])  # fsegment
                foff = str(df.iloc[k, 9])  # foffset
                tseg = str(df.iloc[k, 10])  # tsegment
                toff = str(df.iloc[k, 11])  # toffset

                if f[0].isdigit() == True:
                    # index = k
                    new_index = k + 1
                    [f1, f2] = f.split("\r", 1)
                    [fs, fo] = f1.split("/", 1)
                    [t1, t2] = t.split("\r", 1)
                    [ts, to] = t1.split("/", 1)
                    [m1, m2] = m.split("\r", 1)

                    replacement_row = [p, s, f2, t2, sc, m1, mu, a, fseg, foff, tseg, toff]
                    # fmt: off
                    new_row =         [p, s, f2, t2, sc, m2, mu, a, fs, fo, ts, to]

                    for a in range(0, len(replacement_row)):
                        df.loc[k, a] = replacement_row[a]
                    df = Insert_row(new_index, df, new_row)

                    print(df.iloc[k])
                    print(df.iloc[k + 1])

        # frames.append(table)

        # allpgs = pd.concat(frames)
        # allpgs.to_csv('D:/dvrpc_shared/BFR_Tracking/paving_package/CSVs/%s.csv' % filenames[j])
