__author__ = 'kostas'

OPTIMIZE_RUNTIME = \
    r"""
    """

ADD_RUNTIME = \
    r"""
    -- create extension plpythonu;

    CREATE TYPE lp_result AS (
        cvl_id bigint,
        cvl_rank double precision,
        lp_value double precision
    );

    CREATE OR REPLACE FUNCTION CVL_LP
    (
      conflict_table text
    ) RETURNS SETOF lp_result AS
    $$
        import cvxopt
        from math import ceil, floor
        from cvxopt import matrix, spmatrix, sparse, solvers

        SELECT_CONFLICTS = \
            (
                "SELECT"
                " array_agg(cvl_id) as rids,"
                " (SELECT min_hits FROM {conflict_table} t2 WHERE t1.conflict_id = t2.conflict_id LIMIT 1)"
                " FROM"
                " {conflict_table} t1"
                " GROUP BY"
                " conflict_id"
            )

        # get conflicts
        sql = SELECT_CONFLICTS.format(conflict_table=conflict_table)
        conflicts = plpy.execute(sql)
        if not conflicts:
            return

        # get variables
        sql = "SELECT cvl_id as rid, min(cvl_rank) as rank FROM {conflict_table} GROUP BY cvl_id".format(
            conflict_table=conflict_table)
        rids_and_ranks = plpy.execute(sql)
        rid_lookup = {}
        for i, row in enumerate(rids_and_ranks):
            rid_lookup[row['rid']] = {'rank': row['rank'], 'pos': i}

        # b: non-neg, less-than-one, min_hits
        _b = matrix([0.0] * len(rids_and_ranks) + [1.0] * len(rids_and_ranks) + [-c['min_hits'] for c in conflicts])

        # c: ranks
        _c = matrix([row['rank'] for row in rids_and_ranks])

        # A:
        non_neg = spmatrix(-1.0, range(len(rids_and_ranks)), range(len(rids_and_ranks)))
        less_than_one = spmatrix(1.0, range(len(rids_and_ranks)), range(len(rids_and_ranks)))
        I = []
        J = []
        for i, cflt in enumerate(conflicts):
            for rid in cflt['rids']:
                I.append(i)
                J.append(rid_lookup[rid]['pos'])
        csets = spmatrix(-1.0, I, J)

        _A = sparse([non_neg, less_than_one, csets])

        solvers.options['show_progress'] = False
        sol = solvers.lp(_c, _A, _b)

        if sol['status'] == 'optimal':
            for i, lp_value in enumerate(sol['x']):
                cvl_id = rids_and_ranks[i]['rid']
                cvl_rank = rids_and_ranks[i]['rank']
                yield {'cvl_id': cvl_id, 'cvl_rank': cvl_rank, 'lp_value': lp_value}
        else:
            plpy.error("Infeasible LP instance detected by solver!")

    $$ LANGUAGE plpythonu VOLATILE;

    CREATE OR REPLACE FUNCTION CVL_LPBOUND
    (
        conflict_table text
    ) RETURNS double precision AS
    $$
        SELECT sum(lp_value * cvl_rank) FROM CVL_LP('_conflicts');
    $$ LANGUAGE sql VOLATILE;


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

    CREATE OR REPLACE FUNCTION CVL_CellForPoint
    (
      geom geometry,
      cell_size float8,
      x0 float8 DEFAULT -20037508.34,
      y0 float8 DEFAULT -20037508.34,
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


    CREATE OR REPLACE FUNCTION CVL_RasterToPoints
    (
        the_raster raster,
        OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
    SELECT
        ST_Translate(
            PT.pt,
            (IDX.i - 1) * ST_PixelWidth($1),
            (IDX.j - 1) * ST_PixelHeight($1)
        )
    FROM
        (SELECT
            generate_series(1, ST_Width($1)) AS i,
            generate_series(1, ST_Height($1)) AS j
        ) IDX,
        (SELECT
        ST_SetSrid(
                ST_Point(
                    ST_UpperLeftX($1) + (ST_PixelWidth($1) / 2),
                    ST_UpperLeftY($1) + (ST_PixelHeight($1) / 2)
                ),
                ST_SRID($1)
            ) as pt
        ) PT
    WHERE
        ST_Value($1,IDX.i,IDX.j) = 1
    $$ LANGUAGE sql IMMUTABLE STRICT;


    CREATE OR REPLACE FUNCTION CVL_CellsForPolygon
    (
      geom geometry,
      cell_size double precision,
      x0 double precision DEFAULT -20037508.34,
      y0 double precision DEFAULT -20037508.34,
      OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
    SELECT
        CVL_RasterToPoints(
            ST_AsRaster(
                $1,
                $2,
                $2,
                $3,
                $4,
                '1BB',
                1::double precision,
                0::double precision,
                0::double precision,
                0::double precision,
                true)) pt
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
        WHEN GeometryType($1)='POINT' THEN CVL_CellForPoint($1, CVL_CellSizeZ($2))
        ELSE CVL_CellsForPolygon($1, CVL_CellSizeZ($2))
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

REMOVE_RUNTIME = \
    """
    DROP FUNCTION CVL_LP(text);
    DROP FUNCTION CVL_LPBound(text);
    DROP TYPE lp_result;
    DROP FUNCTION CVL_PointHash(geometry);
    DROP FUNCTION CVL_WebMercatorCells(geometry, integer);
    DROP FUNCTION CVL_CellsForPolygon(geometry, float8, float8, float8);
    DROP FUNCTION CVL_CellForPoint(geometry, float8, float8, float8);
    DROP FUNCTION CVL_ResZ(integer,integer);
    DROP FUNCTION CVL_CellSizeZ(integer);
    """