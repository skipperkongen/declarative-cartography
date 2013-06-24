SET_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- set up

    CREATE TEMPORARY TABLE _cellbound_cells AS
    (
        SELECT
            CVL_PointHash(CVL_WebMercatorCells({geometry}, {z})) || cvl_partition AS cell_id,
            cvl_id,
            cvl_rank,
            cvl_partition
        FROM
            {level_view}
    );
    """

FIND_CONFLICTS = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- find conflicts
    SELECT
        exceeded_cells.cell_id as conflict_id,
        all_cells.cvl_id,
        all_cells.cvl_partition,
        all_cells.cvl_rank,
        exceeded_cells.min_hits
    FROM
        _cellbound_cells all_cells
    JOIN
    (
        -- Find all cells with more than K records belonging to the same partition
        SELECT
            cell_id,
            count(*) - {parameter_1} AS min_hits
        FROM
            _cellbound_cells
        GROUP BY
            cell_id
        HAVING
            count(*) > {parameter_1}
    ) exceeded_cells
    ON all_cells.cell_id = exceeded_cells.cell_id
    """

CLEAN_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- clean up

    DROP TABLE _cellbound_cells;
    """
