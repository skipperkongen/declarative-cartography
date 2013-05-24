# Evaluating cellbound constraint

Problem: Given a uniform grid of cells, find all cells intersecting more than *K* records and delete records to make each cell feasible

## SQL

Continuing with the [example from README](../README.md):

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

The constraint is evaluated over a table cph_highway_output

```sql
-- Make sure _records_to_delete exists
CREATE TEMPORARY TABLE IF NOT EXISTS _records_to_delete(ogc_fid int);

-- create temp table with cell-id for all records at zoom-level Z
CREATE TEMPORARY TABLE _cellbound_tmp AS 
SELECT
	ogc_fid,
    ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( CURRENT_Z ), 0, 0 )) AS cell_id,
	_partition,
	_rank
FROM 
	cph_highway_output
WHERE 
	tile_level = CURRENT_Z;

-- Find records to delete
WITH conflicts AS
(
    SELECT cell_id || _partition AS conflict
    FROM _cellbound_tmp
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






