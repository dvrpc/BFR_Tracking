####
# TO DO:
# iterate over multiple package pdfs in folder
# need a way to flag and fix multipiece segments

import tabula
import pandas as pd
from PyPDF2 import PdfFileReader

#run on multiple files in folder
file = 'D:\dvrpc_shared\BFR_Tracking\paving_package\Location Summary C12.pdf'

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

    frames.append(table)



allpgs = pd.concat(frames)
allpgs.to_csv('D:/dvrpc_shared/BFR_Tracking/test.csv')





