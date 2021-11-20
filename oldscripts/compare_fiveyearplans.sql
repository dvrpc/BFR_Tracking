WITH tblA AS(
	SELECT *
	FROM public."FiveYr_Plan_19-23"
	WHERE county = 'Bucks'
	AND "year" = 2020
	),
tblB AS(
	SELECT *
	FROM public."FiveYr_Plan_20-24"
	WHERE county = 'Bucks'
	AND year = 2020
	)
SELECT
	a.stateroute,
	a.loc,
	a.intersectionfrom,
	a.intersectionto,
	a.plannedmiles,
	b.intersectionfrom,
	b.intersectionto,
	b.plannedmiles
FROM tblA a
INNER JOIN tblB b
ON a.stateroute = b.stateroute
AND a.loc = b.loc



--compare using shortcodes
WITH tblA AS(
    SELECT
        *,
        CONCAT(CAST(stateroute AS text),segfrom, segto) AS shortcode,
        CONCAT(CAST(stateroute AS text), segfrom, offsetfrom, segto, offsetto) AS longcode
    FROM public."FiveYr_Plan_19-23"
    ),
tblB AS(
        SELECT
        *,
        CONCAT(CAST(stateroute AS text),segfrom, segto) AS shortcode,
        CONCAT(CAST(stateroute AS text), segfrom, offsetfrom, segto, offsetto) AS longcode
    FROM public."FiveYr_Plan_20-24"
    )
    
--these records have not changed
SELECT 
    a.*,
    b.year,
    b.plannedmiles,
    b.shortcode,
    b.longcode
FROM tblA a
INNER JOIN tblB b
ON a.longcode = b.longcode
WHERE a.year = b.year
AND a.plannedmiles = b.plannedmiles
ORDER BY a.year, a.county

--these records cover the same segments, but have different offsets, thus different planned miles
SELECT 
    a.*,
    b.year,
    b.plannedmiles,
    b.shortcode,
    b.longcode
FROM tblA a
INNER JOIN tblB b
ON a.shortcode = b.shortcode
WHERE a.longcode <> b.longcode
ORDER BY a.year, a.county

--these records have changed years, but extents are the same
SELECT 
    a.*,
    b.year,
    b.plannedmiles,
    b.shortcode,
    b.longcode
FROM tblA a
INNER JOIN tblB b
ON a.longcode = b.longcode
WHERE a.year <> b.year
--WHERE a.year > b.year (these records have moved to an earlier year) 
--WHERE a.year < b.year (these records have moved to a later year) 
ORDER BY a.year, a.county

--these records were in the previous plan and are not in the new plan
SELECT 
    a.*
FROM tblA a
WHERE NOT EXISTS(
	SELECT *
	FROM tblB b
	WHERE a.shortcode = b.shortcode
	)
--not including those in old years that would be removed
-- AND a.year NOT IN (2018, 2019)
ORDER BY a.year, a.county

--these records are new to the plan 
SELECT 
    b.*
FROM tblB b
WHERE NOT EXISTS(
	SELECT *
	FROM tblA a
	WHERE a.shortcode = b.shortcode
	)
ORDER BY b.year, b.county


--where the longcode is the same, the milesage is also always the same
--these have the same short code, but different long codes, and therefore, different mileage
--***none in this case***
SELECT 
    a.*,
    b.year,
    b.plannedmiles,
    b.shortcode,
    b.longcode
FROM tblA a
INNER JOIN tblB b
ON a.shortcode = b.shortcode
WHERE a.year = b.year
AND a.plannedmiles <> b.plannedmiles
ORDER BY a.year, a.county


---add column with codes to represent changes between years
--only need to add codes to new list
--CODES--
--No change from previous plan                 = 0
--Length of segment changed from previous plan = 1
--Moved to earlier year                        = 2
--Moved to later year                          = 3
--New to plan (including new future year)      = 4

ALTER TABLE public."FiveYr_Plan_20-24"
ADD COLUMN changecode numeric;
COMMIT;

--add columns to hold short and long codes
ALTER TABLE public."FiveYr_Plan_19-23"
ADD COLUMN shortcode text;
ALTER TABLE public."FiveYr_Plan_19-23"
ADD COLUMN longcode text;
COMMIT;

ALTER TABLE public."FiveYr_Plan_20-24"
ADD COLUMN shortcode text;
ALTER TABLE public."FiveYr_Plan_20-24"
ADD COLUMN longcode text;
COMMIT;

--populate short and long codes
UPDATE public."FiveYr_Plan_19-23"
SET shortcode = CONCAT(CAST(stateroute AS text),segfrom, segto),
	longcode = CONCAT(CAST(stateroute AS text), segfrom, offsetfrom, segto, offsetto)
    
UPDATE public."FiveYr_Plan_20-24"
SET shortcode = CONCAT(CAST(stateroute AS text),segfrom, segto),
	longcode = CONCAT(CAST(stateroute AS text), segfrom, offsetfrom, segto, offsetto)
    
--no change
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 0
FROM (
    SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
    ON a.longcode = b.longcode
    WHERE a.year = b.year
    AND a.plannedmiles = b.plannedmiles
        ) AS subquery
WHERE public."FiveYr_Plan_20-24".longcode = subquery.longcode;

--length change
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 1
FROM (
	SELECT 
	    a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
	ON a.shortcode = b.shortcode
	WHERE a.longcode <> b.longcode
        ) AS subquery
WHERE public."FiveYr_Plan_20-24".longcode = subquery.longcode;

--moved to earlier year
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 2
FROM (
    SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
    ON a.longcode = b.longcode
    WHERE a.year < b.year
        ) AS subquery
WHERE public."FiveYr_Plan_20-24".longcode = subquery.longcode;

--moved to later year
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 3
FROM (
    SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
    ON a.longcode = b.longcode
    WHERE a.year > b.year
        ) AS subquery
WHERE public."FiveYr_Plan_20-24".longcode = subquery.longcode;

--new to plan (including 2024 records)
UPDATE public."FiveYr_Plan_20-24"
SET changecode = 4
FROM (
    SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    WHERE NOT EXISTS(
        SELECT *
        FROM public."FiveYr_Plan_19-23" b
        WHERE a.shortcode = b.shortcode
        )
        ) AS subquery
WHERE public."FiveYr_Plan_20-24".longcode = subquery.longcode;


--summarize changes
SELECT county, year, changecode, count(*)
FROM public."FiveYr_Plan_20-24" 
--WHERE year = 2020
--AND county = 'Bucks'
GROUP BY county, year, changecode
ORDER BY county, year, changecode

--example of seeing which records we need to look at more closely
SELECT *
FROM public."FiveYr_Plan_20-24" 
WHERE year = 2020
AND county = 'Montgomery'
AND changecode = 4


--what to do with those that were pushed forward from 2020 or were in 2020 but are now removed from plan all together
--in Db, if they are in this list, leave them in 2020
	SELECT *
	FROM public."FiveYr_Plan_20-24"
	WHERE county = 'Bucks'
	AND year = 2020
	ORDER BY loc

--if they are in this list, change their year to a future year
   SELECT 
        a.*
    FROM public."FiveYr_Plan_20-24" a
    INNER JOIN public."FiveYr_Plan_19-23" b
    ON a.longcode = b.longcode
    WHERE a.year > b.year
    AND b.year = 2020
    AND a.county = 'Bucks'
    ORDER BY loc
--if they are in neither list, remove them DB