class CellBoundK(object):
	"""docstring for CellBoundK"""
	def __init__(self, **kwargs):
		super(CellBoundK, self).__init__()
		self.k = kwargs.get('k', 8)
	
	def setup(self, **kwargs):
		return """-- CELLBOUND at Z={current_z}
-- Cellbound constraint: setup
CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify({geometry}, ST_CellSizeZ( {current_z} ), 0, 0 )) || _partition AS cell_id,
		{id} AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = {current_z}
);		
""".format(**kwargs)

	def find_conflicts(self, **kwargs):
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
		count(*) - {k} AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > {k}
) f 
ON c.cell_id = f.cell_id;
""".format(**kwargs)
	
	def clean_up(self, **kwargs):
		return """--Cellbound constraint: clean up
DROP TABLE _cellbound_1;
""".format(**kwargs)

if __name__ == '__main__':
	params = {'current_z': 15, 'k':16, 'geometry': 'wkb_geometr', 'id': 'ogc_fid'}
	cb = CellBoundK(**params)
	
	print cb.setup(**params)
	print cb.find_conflicts(**params)
	print cb.clean_up(**params)
