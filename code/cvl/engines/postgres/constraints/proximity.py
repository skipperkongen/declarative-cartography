SET_UP = \
    """
    """

FIND_CONFLICTS = \
    """
    ---------------------------
    -- proximity constraints --
    ---------------------------
    -- find conflicts

    SELECT
        ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id,
        Unnest(array[l.{fid}, r.{fid}]) AS {fid},
        Unnest(array[l.cvl_rank, r.cvl_rank]) AS cvl_rank,
        Unnest(array[l.cvl_partition, r.cvl_partition]) AS cvl_partition,
        1 as min_hits
    FROM
        {output} l
    JOIN
        {output} r
    ON
        l.{fid} < r.{fid}
    AND	l.cvl_zoom <= {z}
    AND	r.cvl_zoom <= {z}
    -- AND l.cvl_partition = r.cvl_partition
    AND	ST_DWithin(l.{geometry}, r.{geometry}, CVL_ResZ({z}, 256) * {parameter_1})
    """

CLEAN_UP = \
    """
    """

