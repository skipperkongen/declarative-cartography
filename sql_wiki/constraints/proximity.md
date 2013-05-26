# Evaluating proximity constraint

Problem: Make sure no two records are too close to each other (in pixels).

As for all constraints, the aim is to populate the temporary *_conflicts* table.

## SQL

Using airports as an example.

```sql
CREATE TABLE us_airports_output AS
SELECT 
	*, 
	random() AS _rank, 
	1 AS _partition,
	15 as _tile_level 
FROM us_geocommons_airports;

CREATE INDEX us_airports_output_gist ON us_airports_output USING GIST(wkb_geometry);
```

### Setup

No setup

### Find conflicts

Parameter *CURRENT_Z*, *TABLE*, *ID*, *GEOMETRY* and *PIXELS*:

```sql
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id::text, 
	unnest(array[l.:ID, r.:ID]) AS record_id, 
	unnest(array[l._rank, r._rank]) as record_rank,
	1 as min_hits
FROM 
	:TABLE l JOIN
	:TABLE r
ON 
	l.:ID < r.:ID
AND	l._partition = r._partition
AND ST_DWithin(l.:GEOMETRY, r.:GEOMETRY, ST_ResZ(:CURRENT_Z, 256) * :PIXELS);
-- Total query runtime: 565 ms.
-- 82 rows retrieved.
```









