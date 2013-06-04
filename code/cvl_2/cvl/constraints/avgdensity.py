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
	{output}
WHERE
	_tile_level = {current_z};

CREATE TEMP TABLE _avg_density_sums AS
SELECT 
	sum(ST_Area(ST_Intersection(cells.cell_box, ST_Buffer(output.{geometry}, st_ResZ({current_z}, 256))))) AS itx_area,
	pow(ST_CellSizeZ({current_z}),2) AS cell_area,
	output._partition
FROM 
	{output} output JOIN cells 
ON 
	output.{fid} = cells.{fid} 
AND 
	output._partition = cells._partition
GROUP BY 
	ST_PointHash(ST_Centroid(cells.cell_box)), 
	output._partition;
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
		_partition 
	FROM 
		_avg_density_sums
	GROUP BY 
		_partition
	HAVING 
		Avg(cell_area/itx_area) > {parameter_1}
)
"""

CLEAN_UP = \
"""
DROP TABLE _avg_density_cells;
DROP TABLE _avg_density_sums;
"""
