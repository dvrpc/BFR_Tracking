####
# TO DO:
# need a way to flag and fix multipiece segments

import tabula
import os
import pandas as pd
from PyPDF2 import PdfFileReader

#create list of package files in folder
filepath = 'D:\dvrpc_shared\BFR_Tracking\paving_package\PDFs'
paths = []
filenames = []
for root, dirs, files in os.walk(filepath):
    for f in files: 
        if f.endswith(".pdf"):
            paths.append(os.path.join(root, f))
            filenames.append(os.path.join(f).replace('.pdf',''))

for j in range(0, len(paths)):
    file = paths[j]
    #determine number of pages in PDF
    with open(file, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        num_pgs = pdf_reader.numPages

    #append records from each page to dataframe
    frames = []
    for i in range(1,num_pgs+1):
        table = tabula.read_pdf(file, pages=i)
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

        
        for k in range(0, len(table['from'])):
            f = str(table.iloc[k, 2])
            t = str(table.iloc[k, 3])
            if f[0].isdigit() == True OR t[0].isdigit() == True: 
                print(f, t, 'True')
            else:
                print('False')
        



        #frames.append(table)

    #allpgs = pd.concat(frames)
    #allpgs.to_csv('D:/dvrpc_shared/BFR_Tracking/paving_package/CSVs/%s.csv' % filenames[j])

'''
From/to:
Split segment values out first and then split out where numbers meet letters

How to decide what rows need this extra attention? From/to still start with numbers?

What to do with multiple segments? Flag for manual decision. View and have options specified: keep one (choose which), keep both

What do to with rows? Duplicate if keeping both.

delete bottom row - totals

Compare to 5year plan and update status accordingly
Keep others and mark as not on 5 year plan

How to Split a String Between Numbers and Letters? – Finxter


https://blog.finxter.com/how-to-split-a-string-between-numbers-and-letters/

'''