SET_UP = \
""""""

FIND_CONFLICTS = \
"""
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id, 
	unnest(array[l.{id}, r.{id}]) AS record_id, 
	unnest(array[l._rank, r._rank]) as record_rank,
	1 as min_hits
FROM 
	{table} l 
JOIN
	{table} r
ON 
	l.{id} < r.{id}
AND	l._partition = r._partition
AND	l._tile_level = {current_z}
AND	r._tile_level = {current_z}
AND	ST_DWithin(l.{geometry}, r.{geometry}, ST_ResZ({current_z}, 256) * {_pixels});
"""

CLEAN_UP = \
""""""

class ProximityConstraint(object):
	"""Implementation of constraint 'proximity'"""
	def __init__(self, **query):
		super(ProximityConstraint, self).__init__()
		self.query = query
		# cast _pixels to integer and set default if missing
		self.query['_pixels'] = int(self.query.get('_pixels', 5))

	
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
	query = {'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid', 'pixels': 5}
	cb = ProximityConstraint(**query)
	
	code = []
	code.extend(cb.set_up(current_z = 15))
	code.extend(cb.find_conflicts(current_z = 15))
	code.extend(cb.clean_up(current_z = 15))
	print "".join(code)
