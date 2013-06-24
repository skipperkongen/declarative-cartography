INSTALL = \
    """
    """

SOLVE = \
    """
      -- N Hitting Set heuristic
      SELECT cvl_id
      FROM (
        SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY cvl_rank) AS r, cvl_id, cvl_rank, min_hits
        FROM _conflicts
      ) h
      WHERE h.r <= h.min_hits
    """

UNINSTALL = \
    """
    """