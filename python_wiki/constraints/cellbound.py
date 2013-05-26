class CellBoundK(object):
	"""Implementation of constraint 'cell bound K'"""
	def __init__(self, **query):
		super(CellBoundK, self).__init__()
		self.query = query
	
	def setup(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """-- CELLBOUND at Z={current_z}
-- Cellbound constraint: setup
CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify({geometry}, ST_CellSizeZ( {current_z} ), 0, 0 )) || _partition AS cell_id,
		{id} AS record_id,
		_rank
	FROM 
		{table}
	WHERE 
		_tile_level = {current_z}
);		
""".format(**params)

	def find_conflicts(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """-- Cellbound constraint: find conflicts
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
""".format(**params)
	
	def clean_up(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """--Cellbound constraint: clean up
DROP TABLE _cellbound_1;
""".format(**params)

if __name__ == '__main__':
	query = {'table': 'cph_highway_output', 'geometry': 'wkb_geometr', 'id': 'ogc_fid', '_k':16}
	cb = CellBoundK(**query)
	current_z = 15
	print cb.setup(current_z)
	print cb.find_conflicts(current_z)
	print cb.clean_up(current_z)
