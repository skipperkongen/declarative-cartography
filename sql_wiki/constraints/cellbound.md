# Evaluating cellbound constraint

Problem: Given a uniform grid of cells, find all cells intersecting more than *K* records and delete records to make each cell feasible

As for all constraints, the aim is to populate the temporary *_conflicts* table.

## SQL

Continuing with the [cph_highway](../README.md) example.

With input parameters CURRENT_Z and K: Update temporary table *_records_to_delete*:

```sql
-- create temp table with cell-id for all records at zoom-level Z
CREATE TEMPORARY TABLE _cellbound_cellids AS 
(
	SELECT
		ogc_fid AS record_id,
    	ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( CURRENT_Z ), 0, 0 )) AS cell_id,
		_partition,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = CURRENT_Z;
);

-- Find overfull cells by partition
CREATE TEMPORARY TABLE _cellbound_overfull AS
(
    SELECT cell_id || _partition AS overfull_cell
    FROM _cellbound_cellids
    GROUP BY cell_id, _partition
    HAVING count(*) > K
);

-- Now the hard part: For each overfull cell, create all conflicts...
-- TODO!

-- Drop table
DROP TABLE _cellbound_cellids;
DROP TABLE _cellbound_overfull;
```






