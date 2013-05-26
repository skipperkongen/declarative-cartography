class Proximity(object):
	"""Implementation of constraint 'proximity'"""
	def __init__(self, **query):
		super(Proximity, self).__init__()
		self.query = query
	
	def setup(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """-- proximity constraint at Z={current_z}
-- proximity constraint: setup	(noop)
""".format(**params)

	def find_conflicts(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """-- proximity constraint: find conflicts
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id::text, 
	unnest(array[l.{id}, r.{id}]) AS record_id, 
	unnest(array[l._rank, r._rank]) as record_rank,
	1 as min_hits
FROM 
	{table} l JOIN
	{table} r
ON 
	l.{id} < r.{id}
AND	l._partition = r._partition
AND	l._tile_level = {current_z}
AND	r._tile_level = {current_z}
AND	ST_DWithin(l.{geometry}, r.{geometry}, ST_ResZ({current_z}, 256) * {pixels});
""".format(**params)
	
	def clean_up(self, current_z):
		params = dict(self.query.items() + [('current_z', current_z)])
		return """--proximity constraint: clean up (noop)
""".format(**params)

if __name__ == '__main__':
	query = {'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid', 'pixels': 5}
	cb = Proximity(**query)
	
	print cb.setup(current_z = 15)
	print cb.find_conflicts(current_z = 15)
	print cb.clean_up(current_z = 15)
