# About the SQL wiki

The SQL wiki is a repository of SQL queries I've developed for CVL.

SQL includes:

* [Stored procedures](stored_procedures) for repeated tasks in CVL
* [Algorithms for general problems](algorithms) and specification of input/output
* [SQL statements for evaluating cartographic constraints](constraints). Output is an instance of [hitting set](algorithms/hitting_set.md).


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

Start by creating the output table. Copy records to Z+1 and do not enforce constraints for this level.

Example output table:

```sql
-- Create main table
CREATE TABLE cph_highway_output AS
SELECT 
	*, 
	st_length(wkb_geometry) AS _rank, 
	type AS _partition, 
	15 as _tile_level
FROM 
	cph_highway;
-- 396 ms execution time.
```

Remember to create spatial index on table:

```sql
CREATE INDEX ON cph_highway_output USING GIST(wkb_geometry);
```

### Copy-down

This is how to copy an entire level of records to the next lower scale level, e.g. from level 15 to 14:

```sql
-- Example of level-copy operation 15 -> 14
INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 14 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 15;
```

### Evaluate constraints

Result of evaluating constraints go into a temporary *_conflicts* table. The table acts as an instance of the N Hitting Set Problem.

Before evaluating each constraint, create this table

```sql
CREATE TEMPORARY TABLE _conflicts(conflict_id integer, record_id integer, _rank float, min_hits integer);
```

Executing constraint code should add rows to *_conflicts* table representing the conflicts for the constraint:

```sql
INSERT INTO _conflicts
SELECT c.* FROM ('CONSTRAINT-SELECT') c
-- See constraints folder for select statements for each constraint
```

Use some algorithm for [N Hitting Set](algorithms/hitting_set.md) to find all records that should be deleted:

TODO: The following algorithms should be modified to delete *min_hits* records from each conflict.

```sql
DELETE FROM cph_highway_output 
WHERE 
	_tile_level = CURRENT_Z
AND ogc_fid IN (
	SELECT h.record_id AS ogc_fid 
	FROM (
		SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, c.record_id
    	FROM _conflicts c
	) h
WHERE h.r = 1)
```

After having deleted records for a given constraint, drop the *_conflicts* table. It will be created again before evaluating the next constraint:

```sql
DROP TABLE _conflicts;
```

Repeat these two steps (copy-down and evaluate constraints) all the way to level 0. 

### Finalize output table

At this point simplify all the records in *cph_highway_output* (could do this at each level but with some complication):

```sql
UPDATE cph_highway_output SET wkb_geometry = ST_Simplify(wkb_geometry, ST_ResZ(_tile_level, 256)/2)
-- Should really use another method of simplifying. This is just an example.
-- 5090 ms execution time
```

Finally drop the *_rank* and *_partition* columns;

```sql
ALTER TABLE cph_highway_output DROP COLUMN IF EXISTS _rank, DROP COLUMN IF EXISTS _partition;
```

## Creating vector tiles from the Multi-scale database

TODO




