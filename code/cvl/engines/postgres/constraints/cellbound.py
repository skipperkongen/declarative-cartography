SET_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- set up

    CREATE TEMPORARY TABLE _busted_cells AS
    (
        SELECT
            t.cell_id,
            Unnest(array_agg(t.cvl_id)) as cvl_id
        FROM
        (
        SELECT
            CVL_PointHash(CVL_WebMercatorCells({geometry}, {z})) AS cell_id,
            cvl_id
        FROM
            {level_view}
        ) t
        GROUP BY t.cell_id
        HAVING count(*) > {parameter_1}
    );

    CREATE INDEX _busted_cells_id_idx ON _busted_cells (cell_id);
    --ANALYZE;
    """

FIND_CONFLICTS = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- find conflicts
    SELECT
        _busted_cells.cell_id as conflict_id,
        _busted_cells.cvl_id
    FROM
        _busted_cells
    """

RESOLVE_IF_DELETE = \
    """
    SELECT count(*) - {parameter_1}
    FROM   _busted_cells c
    WHERE  c.cell_id = conflict_id
    """

CLEAN_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- clean up

    DROP TABLE _busted_cells;
    """
