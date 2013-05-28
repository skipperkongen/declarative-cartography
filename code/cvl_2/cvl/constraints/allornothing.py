SET_UP = \
""""""

FIND_CONFLICTS = \
"""
SELECT 
  {id} AS conflict_id, 
  {id} AS record_id, 
  _rank, 
  _partition,
  1 AS min_hits 
FROM 
  {table}
WHERE
  _tile_level = {current_z}
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
      _tile_level= {current_z}
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
      _tile_level = {current_z} + 1
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
	query = {'table': 'us_airports_output','geometry': 'wkb_geometr', 'id': 'ogc_fid'}
	cb = AllOrNothingConstraint(**query)
	
	code = []
	code.extend(cb.set_up(current_z = 15))
	code.extend(cb.find_conflicts(current_z = 15))
	code.extend(cb.clean_up(current_z = 15))
	print "".join(code)
