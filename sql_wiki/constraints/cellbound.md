# Evaluating cellbound constraint

Problem: Given a uniform grid of cells, find all cells intersecting more than *K* records and delete records to make each cell feasible

As for all constraints, the aim is to populate the temporary *_conflicts* table.

## Important

The way this constraint is formulated, a special edition of hitting set must be solved. For each subset (conflict_id) a given number of elements must be hit, i.e. not just one as in hitting set.

## SQL

Continuing with the [cph_highway](../README.md) example.

Set up:

```sql
-- create temp table with cell-id for all records at zoom-level Z
CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 15 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = CURRENT_Z -- e.g. 15
);
```

Find conflict sets:

```sql
SELECT c.cell_id as conflict_id, c.record_id, c._rank, f.min_hits
FROM _cellbound_1 c JOIN
(
	-- Find all cells with more than K records
	SELECT cell_id, count(*) - K AS min_hits
	FROM _cellbound_1
	GROUP BY cell_id
	HAVING count(*) > K
) f 
ON c.cell_id = f.cell_id;
```

Clean up:

```sql
DROP TABLE _cellbound_1;
```






