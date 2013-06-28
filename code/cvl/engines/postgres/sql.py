"""
Temporary tables have a _ prefix
columns generated by CVL have a cvl_ prefix
framework functions have a CVL_ prefix
"""
__author__ = 'kostas'

# BASIC TRANSACTION

BEGIN_TX = \
    """
    BEGIN;
    """

COMMIT_TX = \
    """
    COMMIT;
    """

# INIT


# FRAMEWORK

ADD_FRAMEWORK = \
    r"""
    -- create extension plpythonu;

    -- CVL_CellSizeZ

    CREATE OR REPLACE FUNCTION CVL_CellSizeZ
    (
      z integer,
      OUT meter_per_pixel float
    ) RETURNS float AS
    $$
    SELECT 40075016.68 / power(2, $1)
    $$ LANGUAGE sql IMMUTABLE STRICT;

    -- CVL_PointHash

    CREATE OR REPLACE FUNCTION CVL_PointHash
    (
      pt geometry,
      OUT geohash text
    ) RETURNS text AS
    $$
    SELECT
      ST_GeoHash
      (
        ST_Transform
        (
          $1,
          4326
        )
      ) AS geohash;
    $$ LANGUAGE sql IMMUTABLE STRICT;

    -- CVL_Cellify

    CREATE OR REPLACE FUNCTION CVL_Cellify
    (
      geom geometry,
      cell_size float8,
      x0 float8 DEFAULT 0,
      y0 float8 DEFAULT 0,
      OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
    SELECT
    *
    FROM
    (
      SELECT
        ST_SnapToGrid
        (
          ST_SetSrid
          (
            ST_Point
            (
              ST_XMin($1) + i*$2,
              ST_YMin($1) + j*$2
            ),
            ST_Srid($1)
          ),
          $3 + $2/2,
          $4 + $2/2,
          $2,
          $2
        ) AS pt
      FROM
        generate_series(0, (ceil(ST_XMax( $1 ) - ST_Xmin( $1 )) / $2)::integer) AS i,
        generate_series(0, (ceil(ST_YMax( $1 ) - ST_Ymin( $1 )) / $2)::integer) AS j
    ) PT
    WHERE
      ST_Distance($1, ST_Expand(PT.pt, $2/2)) = 0;
    $$ LANGUAGE sql IMMUTABLE STRICT;

    CREATE OR REPLACE FUNCTION CVL_CellForPoint
    (
      geom geometry,
      cell_size float8,
      x0 float8 DEFAULT 0,
      y0 float8 DEFAULT 0,
      OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
      SELECT ST_SnapToGrid
      (
        $1,
        $3 + $2/2,
        $4 + $2/2,
        $2,
        $2
      );
    $$ LANGUAGE sql IMMUTABLE STRICT;

    -- web mercator cells

    CREATE OR REPLACE FUNCTION CVL_WebMercatorCells
    (
      geom geometry,
      zoom integer,
      OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
    SELECT
      CASE
        WHEN GeometryType($1)='POINT' THEN CVL_CellForPoint($1, CVL_CellSizeZ($2), -20037508.34, -20037508.34)
        ELSE CVL_Cellify($1, CVL_CellSizeZ($2), -20037508.34, -20037508.34)
      END AS pt

    $$ LANGUAGE sql IMMUTABLE STRICT;

    -- CVL_ResZ

    CREATE OR REPLACE FUNCTION CVL_ResZ
    (
      z integer,
      tilesize integer,
      OUT meter_per_pixel float
    ) RETURNS float AS
    $$
    SELECT (40075016.68 / power(2, $1)) / $2
    $$ LANGUAGE sql IMMUTABLE STRICT;
    """

REMOVE_FRAMEWORK = \
    """
    DROP FUNCTION CVL_PointHash(geometry);
    DROP FUNCTION CVL_WebMercatorCells(geometry, integer);
    DROP FUNCTION CVL_Cellify(geometry, float8, float8, float8);
    DROP FUNCTION CVL_CellForPoint(geometry, float8, float8, float8);
    DROP FUNCTION CVL_ResZ(integer,integer);
    DROP FUNCTION CVL_CellSizeZ(integer);
    """

DROP_OUTPUT_TABLE = \
    """
    DROP TABLE IF EXISTS {output};
    """

CREATE_OUTPUT_TABLE_AND_INDEX = \
    """
    CREATE TABLE {output} AS
    SELECT
      {fid}::bigint as cvl_id, {geometry}, {other}
      {rank_by}::float AS cvl_rank,
      {partition_by} AS cvl_partition,
      0 as cvl_zoom
    FROM
      {input};

    CREATE INDEX {output}_zidx ON {output} (cvl_zoom);
    CREATE INDEX {output}_gist ON {output} USING GIST({geometry});
    """

# CVL

MERGE_PARTITIONS = \
    """
    UPDATE {output} SET cvl_partition = '{after_merge}' WHERE cvl_partition IN ({before_merge});
    """

MERGE_PARTITIONS_REST = \
    """
    UPDATE {output} SET cvl_partition = '{after_merge}' WHERE cvl_partition NOT IN ({merged});
    """

# Stage commands

CREATE_TEMP_TABLES_FOR_LEVEL = \
    """
    CREATE TEMPORARY TABLE _conflicts (conflict_id text, cvl_id bigint, cvl_rank float, min_hits integer);
    CREATE TEMPORARY TABLE _deletions (cvl_id bigint);
    CREATE TEMPORARY VIEW _level_view AS SELECT * FROM {output} WHERE cvl_zoom = 0;
    """


FORCE_LEVEL = \
    """
    UPDATE {output}
    SET cvl_zoom = {z} + 1
    WHERE cvl_partition = {delete_partition};
    """

FIND_CONFLICTS = \
    """
    INSERT INTO _conflicts
    SELECT
        conflicts.conflict_id,
        conflicts.cvl_id,
        level.cvl_rank,
        conflicts.min_hits
    FROM ({constraint_select}) conflicts
    JOIN _level_view level
    ON conflicts.cvl_id = level.cvl_id;
    """

SOLVE = \
    """
    INSERT INTO _deletions
    SELECT sol.cvl_id FROM ({solution}) sol;
    """

DO_DELETIONS = \
    """
    UPDATE {output}
    SET cvl_zoom = {z} + 1
    WHERE cvl_id IN (SELECT cvl_id FROM _deletions);
    """

ALLORNOTHING = \
    """
    UPDATE {output}
    SET cvl_zoom = {z} + 1
    WHERE cvl_partition IN
    (
      SELECT DISTINCT cvl_partition FROM {output}
      WHERE cvl_zoom= {z} + 1
    );
    """

DROP_TEMP_TABLES_FOR_LEVEL = \
    """
    DROP TABLE _conflicts;
    DROP TABLE _deletions;
    DROP VIEW _level_view;
    """

# COMMENTS

COMMENT = "-- {comment}"


DO_LOG = \
    r"""
    DO $$
        from datetime import datetime
        with open('{log_path}', 'a+') as f:
            to_write = " ".join([datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f"), '{message}'])
            f.write(to_write)
            f.write('\n')
    $$ LANGUAGE plpythonu;
    """

DO_LOG_STATS = \
    r"""
    DO $$
        from datetime import datetime
        sql = "SELECT cvl_zoom, cvl_partition, Count(*) AS num_recs, Sum(cvl_rank) AS aggrank \
               FROM {output} GROUP BY cvl_zoom, cvl_partition ORDER BY cvl_zoom;"
        rows = plpy.execute(sql)
        with open('{log_path}', 'a+') as f:
            for row in rows:
                to_write = " ".join([datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f"), '{job_name}', "stats", str(row)])
                f.write(to_write)
                f.write('\n')
    $$ LANGUAGE plpythonu;
    """

DO_LOG_STATS2 = \
    r"""
    DO $$
        from datetime import datetime
        sql = "SELECT Sum(cvl_rank) AS aggrank \
               FROM {output};"
        rows = plpy.execute(sql)
        with open('{log_path}', 'a+') as f:
            for row in rows:
                to_write = " ".join([datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f"), '{job_name}', "stats2", str(row)])
                f.write(to_write)
                f.write('\n')
    $$ LANGUAGE plpythonu;
    """

TRYTHIS = \
    """
    -- Records per zoom-level:
    -- SELECT cvl_zoom, cvl_partition, Count(*)
    -- FROM {output} GROUP BY cvl_zoom, cvl_partition ORDER BY cvl_zoom, cvl_partition;

    -- Aggregated rank per zoom-level:
    -- SELECT cvl_zoom, Sum(cvl_rank) FROM {output} GROUP BY cvl_zoom ORDER BY cvl_zoom
    """
