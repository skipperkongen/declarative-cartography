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
		tile_level = CURRENT_Z;
)

-- Find overfull cells
CREATE TEMPORARY TABLE _cellbound_overfull AS
(
    SELECT cell_id || _partition AS conflict
    FROM _cellids
    GROUP BY cell_id, _partition
    HAVING count(*) > K
)




INSERT INTO _records_to_delete
SELECT DISTINCT t.ogc_fid -- DELETE THESE RECORDS
FROM
(
    SELECT 
        row_number() OVER (PARTITION BY cell_id,_partition ORDER BY _rank DESC) r, 
        ogc_fid 
    FROM _cellbound_tmp
    WHERE 
        cell_id || _partition IN (select conflict from conflicts)
) t
WHERE t.r > K;

-- Drop table
DROP TABLE _cellbound_tmp;
```






