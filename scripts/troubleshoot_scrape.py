"""
troubleshoot_scrape.py
------------------

This is a collection of lines of code that should be run individually as described; ideally in a notebook.
It is to be used when the tabula pdf scrape pulls wonky, unusable data and the scrape packages script fails.
"""
#if the failed PDF is more than one page, save each page seperately

#add the following to the end  of the 'read_single_page_from_pdf' function to get an output of the failed tabula read
data_folder = Path("./data")
paving_package = data_folder / "paving_package"
output_folder = paving_package / "test"
output_filepath = output_folder / f"{filepath.stem}.csv"
df.to_csv(output_filepath, index=False)


#manually edit the failed read csv to match the format of the cleaned import and save
#read the edited CSV into a dataframe and import into DB
df = pd.read_csv('D:/dvrpc_shared/BFR_Tracking/data/paving_package/test/Location Summary M122.csv')
df.to_sql("Location Summary M122", ENGINE, if_exists="replace")

#if more than one page, create a new table that combines the successfully scraped page and the failed/manually edited page into a single database table with the proper naming convention
q_union = """CREATE TABLE "Location Summary M12" AS(
    select *
    from "Location Summary M121" lsm 
    union all
    select index, 
        project_num , 
        "SR_name" ,
        "from", 
        "to" , 
        "scope" , 
        cast(miles as varchar) as miles, 
        muni, 
        adt, 
        cast(sr as varchar) as sr, 
        name, 
        muni1, 
        muni2, 
        muni3, 
        cast(fsegment as varchar) as fsegment, 
        cast(foffset as varchar) as foffset, 
        cast(tsegment as varchar) as tsegment, 
        cast(toffset as varchar) as toffset 
    from "Location Summary M122" lsm2 
)
"""
ENGINE.execute(q_union)


