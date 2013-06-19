SOLVER = \
"""
  -- N Hitting Set heuristic
  SELECT {fid}, _rank
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, {fid}, _rank, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits
"""
