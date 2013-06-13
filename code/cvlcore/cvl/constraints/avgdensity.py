SET_UP = \
"""
-- averate density constraint

CREATE TEMP TABLE _avg_density_cells AS
SELECT
	ST_Envelope(
		ST_Buffer(
			ST_WebMercatorCells({geometry}, {current_z})),
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
	{output} output JOIN _avg_density_cells cells 
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
	_partition,
	_rank,
	1 as min_hits
FROM 
	{output}
WHERE
	_tile_level = {current_z} AND
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
		Avg(itx_area/cell_area) > {parameter_1}
)
"""

CLEAN_UP = \
"""
DROP TABLE _avg_density_cells;
DROP TABLE _avg_density_sums;
"""
