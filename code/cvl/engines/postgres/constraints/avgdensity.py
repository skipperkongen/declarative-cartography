SET_UP = \
    """
    --------------------------------
    -- average density constraint --
    --------------------------------
    -- setup

    CREATE TEMP TABLE _avg_density_cells AS
    SELECT
        ST_Envelope(
            ST_Buffer(
                CVL_WebMercatorCells({geometry}, {z})),
                CVL_CellSizeZ({z})/2
            )
        ) AS cell_box,
        {fid},
        cvl_partition
    FROM
        {output}
    WHERE
        cvl_zoom <= {z};

    CREATE TEMP TABLE _avg_density_sums AS
    SELECT
        sum(ST_Area(ST_Intersection(cells.cell_box, ST_Buffer(output.{geometry}, CVL_ResZ({z}, 256))))) AS itx_area,
        pow(CVL_CellSizeZ({z}),2) AS cell_area,
        output.cvl_partition
    FROM
        {output} output JOIN _avg_density_cells cells
    ON
        output.{fid} = cells.{fid}
    AND
        output.cvl_partition = cells.cvl_partition
    GROUP BY
        CVL_PointHash(ST_Centroid(cells.cell_box)),
        output.cvl_partition;
    """

FIND_CONFLICTS = \
    """
    --------------------------------
    -- average density constraint --
    --------------------------------
    -- find conflicts

    SELECT
        {fid} as conflict_id,
        {fid},
        cvl_partition,
        cvl_rank,
        1 as min_hits
    FROM
        {output}
    WHERE
        cvl_zoom = {z} AND
        cvl_partition IN
    (
        -- Find all cells, partitions high average density
        SELECT
            cvl_partition
        FROM
            cvl_avg_density_sums
        GROUP BY
            cvl_partition
        HAVING
            Avg(itx_area/cell_area) > {parameter_1}
    )
    """

CLEAN_UP = \
    """
    --------------------------------
    -- average density constraint --
    --------------------------------
    -- clean up

    DROP TABLE _avg_density_cells;
    DROP TABLE _avg_density_sums;
    """
