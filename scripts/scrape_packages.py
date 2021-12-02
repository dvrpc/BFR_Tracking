####
# TO DO:
# need a way to flag and fix multipiece segments
# delete bottom row - totals
from pathlib import Path
import tabula
import os
import pandas as pd
from PyPDF2 import PdfFileReader

pdf_folderpath = './data/paving_package'

#function to insert row into DF
def Insert_row(row_number, df, row_values):
    df1 = df[0:row_number]
    df2 = df[row_number:]
    #for v in range(0, len(row_values)):
    df1.loc[row_number] = row_values
    df_result = pd.concat([df1, df2], ignore_index=True)
    #df_result.reset_index(drop = True)
    return df_result


for filepath in Path(pdf_folderpath).rglob("*.pdf"):

    #determine number of pages in PDF
    with open(filepath, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        num_pgs = pdf_reader.numPages

    #append records from each page to dataframe
    frames = []
    for i in range(1,num_pgs+1):
        table = tabula.read_pdf(filepath, pages=i)
        table = table[0]
        #rename columne
        table.columns = ['project_num', 'SR_name', 'from', 'to', 'scope', 'miles', 'muni', 'adt' ]
        #drop rows 1 & 2 and column 1 (with assigned row numbers)
        table = table.iloc[2: , :]

        #parse out segment/offset from 'from' and 'to' columns for mapping
        table[['fsegment', 'from']] = table['from'].str.split("\r", n=1, expand = True)
        table[['fsegment','foffset']] = table['fsegment'].str.split("/", n=1, expand = True)
        table[['tsegment', 'to']] = table['to'].str.split("\r", n=1, expand = True)
        table[['tsegment','toffset']] = table['tsegment'].str.split("/", n=1, expand = True)

    
        #split out rows with multiple segment/offsets into replacement and new rows
        for k in range(0, len(table['from'])):
            p =    str(table.iloc[k, 0]) #project_num
            s =    str(table.iloc[k, 1]) #sr_name
            f =    str(table.iloc[k, 2]) #from
            t =    str(table.iloc[k, 3]) #to
            sc =   str(table.iloc[k, 4]) #scope
            m =    str(table.iloc[k, 5]) #miles
            mu =   str(table.iloc[k, 6]) #muni
            a =    str(table.iloc[k, 7]) #adt
            fseg = str(table.iloc[k, 8]) #fsegment
            foff = str(table.iloc[k, 9]) #foffset
            tseg = str(table.iloc[k, 10]) #tsegment
            toff = str(table.iloc[k, 11]) #toffset

            if f[0].isdigit() == True:
                #index = k
                new_index = k+1
                [f1, f2] = f.split("\r", 1)
                [fs, fo] = f1.split("/", 1)
                [t1, t2] = t.split("\r", 1)
                [ts, to] = t1.split("/", 1)
                [m1, m2] = m.split("\r", 1)
            
                replacement_row = [p, s, f2, t2, sc, m1, mu, a, fseg, foff, tseg, toff]
                new_row = [p, s, f2, t2, sc, m2, mu, a, fs, fo, ts, to]

                for a in range(0, len(replacement_row)):
                    table.loc[k, a] = replacement_row[a]
                table = Insert_row(new_index, table, new_row)

                print(table.iloc[k])
                print(table.iloc[k+1])

        break    
    break
        

 
            
        




        #frames.append(table)

    #allpgs = pd.concat(frames)
    #allpgs.to_csv('D:/dvrpc_shared/BFR_Tracking/paving_package/CSVs/%s.csv' % filenames[j])





