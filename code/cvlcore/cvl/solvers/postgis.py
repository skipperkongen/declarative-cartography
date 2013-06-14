HITTING_SET_HEURISTIC = \
"""
  -- N Hitting Set heuristic
  SELECT {fid}, _rank
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, {fid}, _rank, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits
"""

class HittingSetHeuristic(object):
	"""docstring for HittingSetHeuristic"""
	def __init__( self ):
		super(HittingSetHeuristic, self).__init__()

	def get_solution( self, query ):
		return [HITTING_SET_HEURISTIC.format( **query.__dict__ )]