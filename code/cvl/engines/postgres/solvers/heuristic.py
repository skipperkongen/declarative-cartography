SOLVER = \
    """
      -- N Hitting Set heuristic
      SELECT {fid}, cvl_rank
      FROM (
        SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY cvl_rank) AS r, {fid}, cvl_rank, min_hits
        FROM _conflicts
      ) h
      WHERE h.r <= h.min_hits
    """
