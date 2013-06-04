SET_UP = \
"""
CREATE TEMP TABLE _avg_density_cells AS
SELECT
	ST_Envelope(
		ST_Buffer(
			ST_Cellify({geometry}, ST_CellSizeZ({current_z}), 0, 0 ),
			ST_CellSizeZ({current_z})/2
		)
	) AS cell_box,
	{fid},
	_partition
FROM 
	{output};
WHERE
	_tile_level = {current_z};

CREATE TEMP TABLE _avg_density_sums AS
SELECT 
	sum(ST_Area(ST_Intersection(c.cell_box, ST_Buffer(h.{geometry}, st_ResZ({current_z}, 256))))) AS itx_area,
	pow(ST_CellSizeZ({current_z}),2) AS cell_area,
	h._partition
FROM 
	cph_highway h JOIN cells 
ON 
	h.{fid} = c.{fid} 
AND 
	h._partition = c._partition
GROUP BY 
	ST_PointHash(ST_Centroid(c.cell_box)), 
	h._partition;
"""

FIND_CONFLICTS = \
"""
-- select records with conflict
SELECT 
	{fid} as conflict_id, 
	{fid} as record_id, 
	_rank,
	_partition,
	1 as min_hits
FROM 
	{output}
WHERE
	_partition IN
(
	-- Find all cells, partitions high average density
	SELECT
		_partition, 
	FROM 
		_avg_density_sums
	GROUP BY 
		_partition
	HAVING 
		Avg(cell_area/itx_area) > {parameter_1}
) foo
"""

CLEAN_UP = \
"""
DROP TABLE _avg_density_cells;
DROP TABLE _avg_density_sums;
"""
