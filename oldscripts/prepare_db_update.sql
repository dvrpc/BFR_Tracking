--Prepare new DB records for import into E.He DB
--output files must be written to same location as Postgres server (daisy), so it will need to be copied to P:\TransitBikePed\OngoingAndMiscWork\SEPA_Suburban_Bike_Lanes_WG\BikeFriendlyResurfacingProgram\Scripts\outputs too

--before having Elizabeth delete anything, guery original DB in Access to determine if 
--any future year records have been modified since they were imported
SELECT 
BIKELANETRACKING_SEPADATA.GISID, 
BIKELANETRACKING_SEPADATA.COUNTY, 
BIKELANETRACKING_SEPADATA.ADMINSELECTED, 
BIKELANETRACKING_SEPADATA.CALENDAR_YEAR, 
BIKELANETRACKING_SEPADATA.STATE_ROUTE, 
BIKELANETRACKING_SEPADATA.ISACTIVE, 
BIKELANETRACKING_SEPADATA.LASTUPDATE
FROM BIKELANETRACKING_SEPADATA
WHERE BIKELANETRACKING_SEPADATA.ADMINSELECTED = "N"
AND (BIKELANETRACKING_SEPADATA.CALENDAR_YEAR = 2021
OR BIKELANETRACKING_SEPADATA.CALENDAR_YEAR = 2022
OR BIKELANETRACKING_SEPADATA.CALENDAR_YEAR = 2023)
AND BIKELANETRACKING_SEPADATA.LASTUPDATE <> #1/8/2019 9:33:51 AM#
ORDER BY BIKELANETRACKING_SEPADATA.CALENDAR_YEAR;


-----DELETE
--first, have E.He delete all records with year >= 2021

-----CHANGE-----
-----CHANGE YEAR-----
--save csv of records to change years for
--set year = 2020 for records where longcode is in this output table
COPY (
	SELECT longcode
	FROM public."FiveYr_Plan_20-24"
	WHERE changecode = 3
	AND year = 2020
	)
TO 'D:\BikePedTransit\BFR\outputs\UpdateYear.csv'
WITH (FORMAT CSV, HEADER)

--update records from new to length change based on results of visual comparison
--be sure to do this before changing anything with those coded as 1 or 4
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 1
WHERE stateroute = '202'
AND loc = 'LOWER YORK RD';

UPDATE public."FiveYr_Plan_20-24"
SET changecode = 1
WHERE stateroute = '1008'
AND loc = 'CURLY HILL RD';

UPDATE public."FiveYr_Plan_20-24"
SET changecode = 1
WHERE stateroute = '1009'
AND loc = 'RED HILL RD'

UPDATE public."FiveYr_Plan_20-24"
SET changecode = 1
WHERE stateroute = '202'
AND loc = 'DEKALB ST'
AND year = 2020

-----CHANGE IDENTIFYING INFORMATION ------
--save csv of records to replace original fields in 2020
--this will have to be done manually (most of the time) because the codes are based on length and will have changed
--includes those with length change (1)
--and those identified in visual check (and manually modified to (1)
COPY (
	SELECT *
	FROM public."FiveYr_Plan_20-24"
	WHERE changecode = 1
	AND year = 2020
	)
TO 'D:\BikePedTransit\BFR\outputs\ChangedLength.csv'
WITH (FORMAT CSV, HEADER)

-----APPEND

--save CSV of records to be appended to DB
COPY(
	--future years
	WITH tblA AS(
		SELECT *
		FROM public."FiveYr_Plan_20-24" f
		WHERE f.year = 2021
		OR f.year = 2022
		OR f.year = 2023
		OR f.year = 2024
		),
	--records to be added to 2020; includes those that were moved earleir (2) and new to plan (4)
	tblB AS(
		SELECT *
		FROM public."FiveYr_Plan_20-24"
		WHERE (changecode = 2
		OR changecode =  4)
		AND year = 2020
		)
	SELECT *
	FROM tblA
	UNION ALL
	SELECT *
	FROM tblB
	)
TO 'D:\BikePedTransit\BFR\outputs\ToAppend.csv'
WITH (FORMAT CSV, HEADER)


--save CSV of records to change years from 2020 to a future year
COPY(
	SELECT *
	FROM public."FiveYr_Plan_20-24"
	WHERE year = 2020
	ORDER BY loc
	)
TO 'D:\BikePedTransit\BFR\outputs\KeepIn2020.csv'
WITH (FORMAT CSV, HEADER)
--save CSV of records to keep in 2020
COPY(
   SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
    ON a.longcode = b.longcode
    WHERE a.year > b.year
    AND b.year = 2020
    ORDER BY loc
	)
TO 'D:\BikePedTransit\BFR\outputs\ChangeYearFrom2020toFuture.csv'
WITH (FORMAT CSV, HEADER)
--remaining records can be deleted (backup in CSV would be helpful since there are notes in some of them)


