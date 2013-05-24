# About the SQL wiki

The SQL wiki is a repository of SQL queries I've developed for CVL.

SQL includes:

* [Stored procedures](stored_procedures) for repeated tasks in CVL
* [Algorithms for general problems](algorithms) and specification of input/output
* [SQL statements for evaluating cartographic constraints](constraint_evaluation). Output is an instance of [hitting set](algorithms/hitting_set.md).


## IMPORTANT!!

This is for creating hitting_set instances!!

```sql
SELECT 1, unnest(array['a', 'b', 'c'])
```

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

### Setting up output table

Start by creating the output table. Copy records to Z+1 and do not enforce constraints for this level:

```sql
-- Create main table
CREATE TABLE cph_highway_output AS
SELECT *, st_length(wkb_geometry) AS _rank, type AS _partition, 15 as tile_level
FROM cph_highway;
-- 396 ms execution time.
```

### Copy records between levels

Next, copy level 15 to 14 (level 15 will contain all records and not be thinned):

```sql
-- Example of level-copy operation 15 -> 14
INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 14 as tile_level
FROM cph_highway_output
WHERE tile_level = 15;
```

### For each constraint

Create temporary *_conflicts* table for collecting conflicts

```sql
CREATE TEMPORARY TABLE _conflicts(conflict_id integer, ogc_fid integer);
```

Execute constraint code and populate *_conflicts* table:

```sql
-- See various queries in constraints
```


Drop *_conflicts* table (will be created again for next level):

```sql
DROP TABLE _conflicts;
```


INSERT INTO _records_to_delete
SELECT * FROM EvalConstraint(constraint, params) -- just for illustration
-- DO:
DELETE FROM cph_high_output 
WHERE ogc_fid in (SELECT * FROM _records_to_delete) AND tile_level = 14
-- END: for each
DROP TABLE _records_to_delete;
```

Repeat all the way up to level 0. 

At this point simplify all the records in *cph_highway_output* (could do this earlier, trading code-simplicity for I/O efficiency):

```sql
UPDATE cph_highway_output SET wkb_geometry = ST_Simplify(wkb_geometry, ST_ResZ(tile_level, 256)/2)
-- Should really use another method of simplifying. This is just an example.
-- 5090 ms execution time
```

Finally drop the *_rank* and *_partition* columns;

```sql
ALTER TABLE cph_highway_output DROP COLUMN IF EXISTS _rank, DROP COLUMN IF EXISTS _partition;
```

Create a vector tile:

```sql
TODO
```




