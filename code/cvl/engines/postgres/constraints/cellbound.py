SET_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- set up

    CREATE TEMPORARY TABLE _cellbound_1 AS
    (
        SELECT
            CVL_PointHash(CVL_WebMercatorCells({geometry}, {z})) || cvl_partition AS cell_id,
            {fid},
            cvl_rank,
            cvl_partition
        FROM
            {output}
        WHERE
            cvl_zoom = {z}
    );
    """

FIND_CONFLICTS = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- find conflicts
    SELECT
        cells.cell_id as conflict_id,
        cells.{fid},
        cells.cvl_partition,
        cells.cvl_rank,
        exceeded.min_hits
    FROM
        _cellbound_1 cells
    JOIN
    (
        -- Find all cells with more than K records
        SELECT
            cell_id,
            count(*) - {parameter_1} AS min_hits
        FROM
            _cellbound_1
        GROUP BY
            cell_id
        HAVING
            count(*) > {parameter_1}
    ) exceeded
    ON cells.cell_id = exceeded.cell_id
    """

CLEAN_UP = \
    """
    --------------------------
    -- cellbound constraint --
    --------------------------
    -- clean up

    DROP TABLE _cellbound_1;
    """
