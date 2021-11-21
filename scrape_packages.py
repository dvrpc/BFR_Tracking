import tabula

#read in paving packages - convert from PDF to excel, read in, and map
#resource: https://towardsdatascience.com/scraping-table-data-from-pdf-files-using-a-single-line-in-python-8607880c750

#run on multiple files in folder
file = 'D:\dvrpc_shared\BFR_Tracking\paving_package\Location Summary C12.pdf'

table = tabula.read_pdf(file, pages=2)

print(table[0])

