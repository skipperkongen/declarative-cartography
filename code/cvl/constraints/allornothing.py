SET_UP = \
""""""

FIND_CONFLICTS = \
"""
SELECT 
  _partition AS conflict_id, 
  {id} AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  {table}
WHERE
  _tile_level = 2 
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {table}
    WHERE 
      _tile_level=2
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {table} 
    WHERE
      _tile_level=3
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);
"""

CLEAN_UP = \
""""""

class AllOrNothingConstraint(object):
	"""Implementation of constraint 'proximity'"""
	def __init__(self, **query):
		super(AllOrNothingConstraint, self).__init__()
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
	query = {'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid'}
	cb = AllOrNothingConstraint(**query)
	
	code = []
	code.extend(cb.set_up(current_z = 15))
	code.extend(cb.find_conflicts(current_z = 15))
	code.extend(cb.clean_up(current_z = 15))
	print "".join(code)
