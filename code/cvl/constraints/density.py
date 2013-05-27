"""Idea: use ratio between the area of a cell, and the area of all buffered 
geometries that intersect the cell. If buffered geometries take up too much 
space, that means that the density is too high."""

Work in progress

SET_UP = \
"""
CREATE TEMPORARY TABLE _density_1 AS 
SELECT 
	ST_Cellify({geometry}, ST_CellSizeZ({current_z}), 0, 0) AS cell_pt, 
	{id} AS record_id,
	_partition
FROM 
	{table}
WHERE
	_tile_level = {current_z};

CREATE TEMPORARY TABLE _density_2 AS
SELECT 
	pow(ST_CellSizeZ({current_z}),2) AS cell_area, 
	ST_Area(ST_Intersection(
		ST_Envelope(ST_Buffer(e.cell_pt, ST_CellSizeZ({current_z})/2)), 
		ST_Buffer(s.{geometry}, ST_ResZ({current_z})))) AS itx_area,
	s.{id},
	s._partition
FROM
	_density_1 e
JOIN
	{table} s
ON
	s.{id} = e.record_id AND
	s._partition = e._partition AND
	s._tile_level = {current_z};
"""

FIND_CONFLICTS = \
"""
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - {_k} AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > {_k}
) f 
ON c.cell_id = f.cell_id;
"""

CLEAN_UP = \
"""
DROP TABLE _density_1;
"""


class DensityConstraint(object):
	"""docstring for DensityConstraint"""
	def __init__(self, **query):
		super(DensityConstraint, self).__init__()
		self.query = query

	def set_up(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return [SET_UP.format(**params)]

	def find_conflicts(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return [FIND_CONFLICTS.format(**params)]
	
	def clean_up(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return [CLEAN_UP.format(**params)]

if __name__ == '__main__':
	query = {'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid', '_maxdensity': 0.5}
	cb = DensityConstraint(**query)
	
	code = []
	code.extend(cb.set_up(current_z = 15))
	code.extend(cb.find_conflicts(current_z = 15))
	code.extend(cb.clean_up(current_z = 15))
	print "".join(code)

	