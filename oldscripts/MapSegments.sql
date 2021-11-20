WITH tblA AS(
	SELECT 
		year,
		to_char(CAST(stateroute AS numeric), 'fm0000') AS sr,
		loc,
		intersectionfrom,
		CAST(segfrom AS numeric) AS sf,
		offsetfrom,
		intersectionto,
		CAST(segto AS numeric) AS st,
		offsetto,
		muni1,
		muni2,
		muni3,
		plannedmiles,
		county,
		county_code,
		shortcode,
		longcode,
		changecode
	FROM "FiveYr_Plan_19-23"
	),

tblB AS(
	SELECT
		st_rt_no,
		cty_code,
		CAST(seg_no AS numeric),
		street_nam,
		bgn_desc,
		end_desc,
		st_transform(geom, 26918) AS geom
	FROM penndot_rms_segments_101518
	),

tblC AS(
	SELECT 
		b.*,
		a.*
	FROM tblB b
	LEFT OUTER JOIN tblA a
	ON a.sr = b.st_rt_no
	AND a.county_code = b.cty_code)

SELECT *
FROM tblC 
WHERE seg_no >= sf
AND seg_no <= st
AND year IS NOT NULL