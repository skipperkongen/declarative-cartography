"""Idea: use ratio between the area of a cell, and the area of all buffered 
geometries that intersect the cell. If buffered geometries take up too much 
space, that means that the density is too high."""

SET_UP = \
"""
CREATE TEMP TABLE _density_1 AS 
SELECT 
	ST_Cellify({geometry}, ST_CellSizeZ({current_z}), 0, 0) AS cell_pt, 
	{id} AS record_id
FROM 
	{table}
WHERE
	_tile_level = {current_z};

CREATE TEMP TABLE _density_2 AS
SELECT
	ST_PointHash(c.cell_pt) AS cell_id,
	ST_Area(ST_Intersection(
		ST_Envelope(
			ST_Buffer(e.cell_pt, ST_CellSizeZ({current_z})/2)), 
		ST_Buffer(t.{geometry}, ST_ResZ({current_z}, 256)))) /
	pow(ST_CellSizeZ({current_z}),2) as relarea,
	t._partition
FROM
	_density_1 d
JOIN
	{table} t
ON
	d.record_id = t.{id}
WHERE
	t._tile_level = {current_z};

CREATE TEMPORARY TABLE _density_3 AS
SELECT 
	DISTINCT _partition
FROM 
	_density_2
GROUP BY
	cell_id,
	_partition
HAVING
	sum(relarea) > {_maxdensity}
"""

FIND_CONFLICTS = \
"""
SELECT 
	{id} AS conflict_id, 
	{id} AS record_id, 
	_rank AS record_rank, 
	1 as min_hits
FROM
	{table}
WHERE 
	_partition IN (SELECT * FROM _density_3)
"""

CLEAN_UP = \
"""
DROP TABLE _density_1;
DROP TABLE _density_2;
DROP TABLE _density_3;
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

	