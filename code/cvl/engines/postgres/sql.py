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

    -- CVL_TimerStart

    CREATE OR REPLACE FUNCTION CVL_TimerStart() RETURNS void AS $$
        import time
        GD['t_last'] = time.time()
        GD['ts'] = []
    $$ LANGUAGE plpythonu;


    -- CVL_TimerLap
    CREATE OR REPLACE FUNCTION CVL_TimerLap(label text) RETURNS double precision AS $$
        import time
        now = time.time()
        if not GD.has_key('t_last'): GD['t_last'] = now
        if not GD.has_key('ts'): GD['ts'] = []
        elapsed = now - GD['t_last']
        GD['t_last'] = now
        GD['ts'].append((label, elapsed))
        return elapsed;
    $$ LANGUAGE plpythonu;

    -- CVL_TimerDump

    CREATE OR REPLACE FUNCTION CVL_TimerDump(path text) RETURNS void AS $$
        with open(path,'w') as f:
            f.write('LABEL,ELAPSED\n')
            f.write('\n'.join( map (lambda x: '{0:s},{1:f}'.format(x[0], x[1]), GD['ts']) ))
    $$ LANGUAGE plpythonu;

    -- CVL_TimerDestroy

    CREATE OR REPLACE FUNCTION CVL_TimerDestroy() RETURNS void AS $$
	if GD.has_key('t_last'): del GD['t_last']
	if GD.has_key('ts'): del GD['ts']
    $$ LANGUAGE plpythonu;

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
    SELECT *
    FROM
    (
      SELECT
        ST_SnapToGrid(
          ST_SetSrid(
            ST_Point(
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
      generate_series(0, (ceil(ST_YMax( $1 ) - ST_Ymin( $1 )) / $2)::integer) AS j) PT
    WHERE
      $1 && ST_Envelope(ST_Buffer(PT.pt, $2/2))
    AND
      ST_Intersects($1, ST_Envelope(ST_Buffer(PT.pt, $2/2)));
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
      CVL_Cellify($1, CVL_CellSizeZ($2), -20037508.34, -20037508.34) as pt
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
    DROP FUNCTION CVL_TimerStart();
    DROP FUNCTION CVL_TimerLap(text);
    DROP FUNCTION CVL_TimerDump(text);
    DROP FUNCTION CVL_TimerDestroy();
    DROP FUNCTION CVL_PointHash(geometry);
    DROP FUNCTION CVL_WebMercatorCells(geometry, integer);
    DROP FUNCTION CVL_Cellify(geometry, float8, float8, float8);
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
      {fid}, {geometry}, {other},
      {rank_by}::float AS cvl_rank,
      {partition_by} AS cvl_partition,
      {zoomlevels} as cvl_zoom
    FROM
      {input};

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

COPY_LEVEL = \
    """
    INSERT INTO {output}
    SELECT {fid}, {geometry}, {other}, cvl_rank, cvl_partition, {z} as cvl_zoom
    FROM {output}
    WHERE cvl_zoom = {copy_from};
    """

CREATE_TEMP_TABLES_FOR_LEVEL = \
    """
    CREATE TEMPORARY TABLE _deletions ({fid} integer, cvl_rank float);
    CREATE TEMPORARY TABLE _conflicts (conflict_id text, {fid} integer, cvl_rank float, min_hits integer);
    """

FORCE_LEVEL = \
    """
    DELETE FROM {output}
    WHERE cvl_zoom = {z}
    AND cvl_partition = {delete_partition};
    """

FIND_CONFLICTS = \
    """
    INSERT INTO _conflicts
    SELECT
        s.conflict_id,
        s.{fid},
        s.cvl_rank,
        s.min_hits
    FROM ({constraint_select}) s;
    """

FIND_CONFLICTS_IGNORE = \
    """
    INSERT INTO _conflicts
    SELECT
        s.conflict_id,
        s.{fid},
        s.cvl_rank,
        s.min_hits
    FROM ({constraint_select}) s
    WHERE s.cvl_partition NOT IN ({ignored_partitions});
    """

COLLECT_DELETIONS = \
    """
    INSERT INTO _deletions
    SELECT sol.{fid}, sol.cvl_rank FROM ({solution}) sol;
    """

DO_DELETIONS = \
    """
    DELETE FROM {output}
    WHERE
        cvl_zoom = {z}
    AND {fid} IN (SELECT {fid} FROM _deletions);
    """

ALLORNOTHING = \
    """
    DELETE FROM {output}
    WHERE cvl_zoom = {z}
    AND cvl_partition IN
    (
      SELECT low.cvl_partition FROM
      (
        SELECT cvl_partition, count(*) AS count
        FROM {output}
        WHERE cvl_zoom= {z}
        GROUP BY cvl_partition
      ) low
      JOIN
      (
        SELECT cvl_partition, count(*) AS count
        FROM {output}
        WHERE cvl_zoom = {z} + 1
        GROUP BY cvl_partition
      ) high
      ON low.cvl_partition = high.cvl_partition
      WHERE low.count < high.count);
    """

SIMPLIFY = \
    """
    UPDATE {output} SET {geometry} = ST_Simplify({geometry}, CVL_ResZ({z}, 256)/2) WHERE cvl_zoom={z};
    """

DROP_TEMP_TABLES_FOR_LEVEL = \
    """
    DROP TABLE _conflicts;
    DROP TABLE _deletions;
    """

# Finalizing

SIMPLIFY_ALL = \
    """
    UPDATE {output} SET {geometry} = ST_Simplify({geometry}, CVL_ResZ(cvl_zoom, 256)/2);
    """

# COMMENTS

COMMENT = "-- {comment}"

TIMER_START = \
    """
    SELECT CVL_TimerStart();
    """

TIMER_LAP = \
    """
    SELECT CVL_TimerLap('{label}');
    """

TIMER_DUMP = \
    """
    SELECT CVL_TimerDump('{path}');
    """

TIMER_DESTROY = \
    """
    SELECT CVL_TimerDestroy();
    """

TRYTHIS = \
    """
    -- Records per zoom-level:
    -- SELECT cvl_zoom, cvl_partition, Count(*)
    -- FROM {output} GROUP BY cvl_zoom, cvl_partition ORDER BY cvl_zoom, cvl_partition;

    -- Aggregated rank per zoom-level:
    -- SELECT cvl_zoom, Sum(cvl_rank) FROM {output} GROUP BY cvl_zoom ORDER BY cvl_zoom
    """
