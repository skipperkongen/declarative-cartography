# About the SQL wiki

The SQL wiki is a repository of SQL queries I've developed for CVL.

SQL includes:

* [Stored procedures](stored_procedures) for repeated tasks in CVL
* [Algorithms for general problems](algorithms) and specification of input/output
* [SQL statements for evaluating cartographic constraints](constraint_evaluation). Output is an instance of [hitting set](algorithms/hitting_set.md).

## Full example

Given at CVL query:

```cvl
GENERALIZE 			{input} -> {output} 

WITH ID 			{column name}
WITH GEOMETRY		{column name}
WITH OTHER			{x, y, z, ...}

AT  				{Z} ZOOM LEVELS

RANK BY 			{float-valued expression}

PARTITION BY 		{expression}

SUBJECT TO 
	 PROXIMITY 		{d} 
THEN CELLBOUND 		{K} 
THEN ALLORNOTHING 

TRANSFORM BY
	SIMPLIFY 
```

And a *concrete* CVL query using the *cph_highway* dataset ([shapefile](http://skipperkongen.dk/geodata/cph_highway.zip)):

```cvl
GENERALIZE 			cph_highway -> cph_highway_output 

WITH ID 			ogc_fid
WITH GEOMETRY		wkb_geometry
WITH OTHER			type, name, lanes, oneway

AT  				15 ZOOM LEVELS

RANK BY 			st_length(wkb_geometry)

PARTITION BY 		type -- this is a column in cph_highway

SUBJECT TO 
	 CELLBOUND 		16
THEN ALLORNOTHING 

TRANSFORM BY
	SIMPLIFY 
```

Start by creating the output table:

```sql
CREATE TABLE cph_highway_output AS
SELECT *, st_length(wkb_geometry) AS _rank, type AS _partition, 15 as tile_level
FROM cph_highway;
-- 396 ms execution time.
```

Next, copy level 15 to 14 (level 15 will contain all records and not be thinned):

```sql
INSERT INTO cph_highway_output AS
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 14 as tile_level
FROM cph_highway_output
WHERE tile_level = 15;
```

Make level 14 feasible and optimal:

```sql
-- MAGIC
```

Repeat all the way up to level 0. 

At this point simplify all the records in *cph_highway_output*:

```sql
UPDATE cph_highway_output SET wkb_geometry = ST_Simplify(wkb_geometry, ST_ResZ(tile_level, 256)/2)
-- Should really use another method of simplifying. This is just an example.
-- 5090 ms execution time
```

Finally drop the *_rank* and *_partition* columns;

```sql
ALTER TABLE cph_highway_output DROP COLUMN IF EXISTS _rank, DROP COLUMN IF EXISTS _partition;
```





