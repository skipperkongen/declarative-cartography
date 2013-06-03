HITTING_SET_HEURISTIC = \
"""
  -- N Hitting Set heuristic
  SELECT h.record_id AS {fid} 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits
"""

class HittingSetHeuristic(object):
	"""docstring for HittingSetHeuristic"""
	def __init__(self, query):
		super(HittingSetHeuristic, self).__init__()
		self.query = query

	def solver_sql(self):
		return [HITTING_SET_HEURISTIC.format(**self.query.__dict__)]