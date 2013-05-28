SET_UP = \
"""
CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify({geometry}, ST_CellSizeZ( {current_z} ), 0, 0 )) || _partition AS cell_id,
		{id} AS record_id,
		_rank,
		_partition
	FROM 
		{table}
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
DROP TABLE _cellbound_1;
"""

class CellboundConstraint(object):
	"""Implementation of constraint 'cell bound K'"""
	def __init__(self, **query):
		super(CellboundConstraint, self).__init__()
		self.query = query
		# cast _k to integer and set default if missing
		self.query['_k'] = int(self.query.get('_k', 8))

	def generate_sql(self, current_z):
		code = []
		code.append(self.set_up(current_z))
		code.append(self.find_conflicts(current_z))
		code.append(self.clean_up(current_z))
		return code
	
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
	query = {'table': 'cph_highway_output', 'geometry': 'wkb_geometr', 'id': 'ogc_fid', '_k':16}
	cb = CellboundConstraint(**query)
	current_z = 15
	code = []
	code.extend(cb.set_up(current_z = 15))
	code.extend(cb.find_conflicts(current_z = 15))
	code.extend(cb.clean_up(current_z = 15))
	print "".join(code)
