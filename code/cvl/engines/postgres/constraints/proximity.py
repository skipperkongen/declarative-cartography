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
        Unnest(array[l.cvl_id, r.cvl_id]) AS cvl_id
    FROM
        {level_view} l
    JOIN
        {level_view} r
    ON
        l.cvl_id < r.cvl_id
    AND l.{geometry} && ST_Expand(r.{geometry}, CVL_ResZ({z}, 256) * {parameter_1})
    AND	ST_Distance(l.{geometry}, r.{geometry}) < CVL_ResZ({z}, 256) * {parameter_1}
    """

RESOLVE_IF_DELETE = \
    """
    1
    """

CLEAN_UP = \
    """
    """

