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
        --ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id,
        l.cvl_id::text || r.cvl_id::text as conflict_id,
        Unnest(array[l.cvl_id, r.cvl_id]) AS cvl_id,
        Unnest(array[l.cvl_rank, r.cvl_rank]) AS cvl_rank,
        Unnest(array[l.cvl_partition, r.cvl_partition]) AS cvl_partition,
        1 as min_hits
    FROM
        {level_view} l
    JOIN
        {level_view} r
    ON
        l.cvl_id < r.cvl_id
    AND l.cvl_partition = r.partition
    AND	ST_DWithin(l.{geometry}, r.{geometry}, CVL_ResZ({z}, 256) * {parameter_1})
    """

CLEAN_UP = \
    """
    """

