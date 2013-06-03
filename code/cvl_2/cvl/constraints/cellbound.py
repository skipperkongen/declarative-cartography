SET_UP = \
"""
CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify({geometry}, ST_CellSizeZ( {current_z} ), 0, 0 )) || _partition AS cell_id,
		{fid} AS record_id,
		_rank,
		_partition
	FROM 
		{output}
	WHERE 
		_tile_level = {current_z}
);
"""

FIND_CONFLICTS = \
"""
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank,
	c._partition
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - {parameter_1} AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > {parameter_1}
) f 
ON c.cell_id = f.cell_id;
"""

CLEAN_UP = \
"""
DROP TABLE _cellbound_1;
"""
