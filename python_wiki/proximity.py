class Proximity(object):
	"""Implementation of constraint 'proximity'"""
	def __init__(self, **kwargs):
		super(Proximity, self).__init__()
		self.pixels = kwargs.get('pixels', 8)
	
	def setup(self, **kwargs):
		return """-- PROXIMITY at Z={current_z}
-- Proximity constraint: setup	(noop)
""".format(**kwargs)

	def find_conflicts(self, **kwargs):
		return """-- Proximity constraint: find conflicts
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
AND ST_DWithin(l.{geometry}, r.{geometry}, ST_ResZ({current_z}, 256) * {pixels});
""".format(**kwargs)
	
	def clean_up(self, **kwargs):
		return """--Proximity constraint: clean up (noop)
""".format(**kwargs)

if __name__ == '__main__':
	params = {'current_z': 15, 'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid', 'pixels': 5}
	cb = Proximity(**params)
	
	print cb.setup(**params)
	print cb.find_conflicts(**params)
	print cb.clean_up(**params)
