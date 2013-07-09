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
                " array_agg(cvl_id) as cvl_ids,"
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
        sql = "SELECT cvl_id, min(cvl_rank) as cvl_rank FROM {conflict_table} GROUP BY cvl_id".format(conflict_table=conflict_table)
        variables = plpy.execute(sql)
        variables = dict(map(
            lambda (pos,x): (x['cvl_id'], {'cvl_rank': x['cvl_rank'], 'pos': pos}),
            enumerate(variables)
        ))
        i_to_var = dict([(value['pos'], key) for (key,value) in variables.items()])

        # b: non-neg, less-than-one, min_hits
        _b = matrix([0.0] * len(variables) + [1.0] * len(variables) + [-c['min_hits'] for c in conflicts])

        # c: ranks
        _c = matrix([variables[v]['cvl_rank'] for v in variables])

        # A:
        non_neg = spmatrix(-1.0, range(len(variables)), range(len(variables)))
        less_than_one = spmatrix(1.0, range(len(variables)), range(len(variables)))
        I = []
        J = []
        for i, cflt in enumerate(conflicts):
            for v in cflt['cvl_ids']:
                I.append(i)
                J.append(variables[v]['pos'])
        csets = spmatrix(-1.0, I, J)

        _A = sparse([non_neg, less_than_one, csets])

        solvers.options['show_progress'] = False
        sol = solvers.lp(_c, _A, _b)

        if sol['status'] == 'optimal':
            for i, lp_value in enumerate(sol['x']):
                cvl_id = i_to_var[i]
                cvl_rank = variables[cvl_id]['cvl_rank']
                yield {'cvl_id': cvl_id, 'cvl_rank': cvl_rank, 'lp_value': lp_value}
        else:
            plpy.error("Infeasible LP instance detected by solver!")

    $$ LANGUAGE plpythonu;

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

    CREATE OR REPLACE FUNCTION CVL_CellsForPolygon
    (
      geom geometry,
      cell_size float8,
      x0 float8 DEFAULT -20037508.34,
      y0 float8 DEFAULT -20037508.34,
      OUT pt geometry
    ) RETURNS SETOF geometry AS
    $$
    SELECT
        ST_SnapToGrid(PT.pt, $3 + $2/2, $4 + $2/2, $2, $2)
    FROM
    (
        SELECT
            ST_SetSrid( ST_Point(ST_XMin($1) + i*$2, ST_YMin($1) + j*$2), ST_Srid($1)) AS pt
        FROM
            generate_series(0, (ceil(ST_XMax( $1 ) - ST_Xmin( $1 )) / $2)::integer) AS i,
            generate_series(0, (ceil(ST_YMax( $1 ) - ST_Ymin( $1 )) / $2)::integer) AS j
    ) PT, (SELECT ST_AsRaster(
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
                true
            ) as raster) RASTER
    WHERE
        ST_Value(RASTER.raster, PT.pt, false) = 1
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