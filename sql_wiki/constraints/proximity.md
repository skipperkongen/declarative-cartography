# Evaluating proximity constraint

Problem: Make sure no two records are too close to each other (in pixels).

As for all constraints, the aim is to populate the temporary *_conflicts* table.

## SQL

Using airports as an example.

```sql
CREATE TABLE us_airports_output AS
SELECT *, random() AS _rank, 1 AS _partition 
FROM us_geocommons_airports;

CREATE INDEX us_airports_output_gist ON us_airports_output USING GIST(wkb_geometry);
```

Compute conflicts with input parameter CURRENT_Z=10 and PIXELS=5:

```sql
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id, 
	unnest(array[l.ogc_fid, r.ogc_fid]) AS record_id, 
	unnest(array[l._rank, r._rank]) as record_rank
FROM 
	airports_output l JOIN
	airports_output r
ON 
	l.ogc_fid < r.ogc_fid
AND	l._partition = r._partition
AND ST_DWithin(l.wkb_geometry, r.wkb_geometry, ST_ResZ(10, 256) * 5);
-- Total query runtime: 546 ms.
-- 82 rows retrieved.
```









