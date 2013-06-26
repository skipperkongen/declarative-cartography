__author__ = 'kostas'

INSTALL = \
    """
    CREATE TYPE cvl_id AS (
      cvl_id bigint
    );

    CREATE OR REPLACE FUNCTION CVL_LPSolver(conflict_table text, lowerbound boolean) RETURNS SETOF cvl_id AS $$
        import cvxopt
        from math import ceil, floor
        from cvxopt import matrix, spmatrix, sparse, solvers

        _SELECT_CONFLICTS = \
            (
                "SELECT"
                " conflict_id,"
                " array_agg(cvl_id) as record_ids,"
                " array_agg(cvl_rank) as record_ranks,"
                " (SELECT min_hits FROM {conflict_table} t2 WHERE t1.conflict_id = t2.conflict_id LIMIT 1)"
                " FROM"
                " {conflict_table} t1"
                " GROUP BY"
                " conflict_id"
            )

        sql = _SELECT_CONFLICTS.format(conflict_table=conflict_table)
        conflicts = plpy.execute(sql)
        if not conflicts:
            return

        # make list of variables
        variables = set()
        RID = 0
        RANK = 1
        for cflt in conflicts:
            if len(cflt['record_ids']) < cflt['min_hits']:
                plpy.notice("Problem! recs: {0:s}, min_hits: {1:d}".format(str(cflt['record_ids']), cflt['min_hits']))
            variables = variables.union(zip(cflt['record_ids'], cflt['record_ranks']))
        variables = list(variables)

        # create index of variables
        vindex = {}
        for i, var in enumerate(variables):
            vindex[var[RID]] = i

        # b: non-neg, less-than-one, min_hits
        _b = matrix([0.0] * len(variables) + [1.0] * len(variables) + [-c['min_hits'] for c in conflicts])
        # c: ranks
        _c = matrix([var[RANK] for var in variables])

        # A:
        non_neg = spmatrix(-1.0, range(len(variables)), range(len(variables)))
        less_than_one = spmatrix(1.0, range(len(variables)), range(len(variables)))
        I = []
        J = []
        for i, cflt in enumerate(conflicts):
            for v in cflt['record_ids']:
                I.append(i)
                J.append(vindex[v])
        csets = spmatrix(-1.0, I, J)

        _A = sparse([non_neg, less_than_one, csets])

        solvers.options['show_progress'] = False
        plpy.notice("Begin LP solver")
        sol = solvers.lp(_c, _A, _b)
        plpy.notice("End LP solver. Status: {0:s}".format(sol['status']))

        EPSILON = 0.00001
        if lowerbound:
            snap = lambda x: (1.0 if x > (1.0 - EPSILON) else 0.0)
        else:
            snap = lambda x: (1.0 if x > EPSILON else 0.0)

        if sol['status'] == 'optimal':
            for i, val in enumerate(sol['x']):
                if snap(val) == 1.0:
                    yield {'cvl_id': variables[i][RID]}
    $$ LANGUAGE plpythonu;
    """

SOLVE = \
    """
    SELECT cvl_id FROM CVL_LPSolver('_conflicts', false)
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_LPSolver(text, boolean);
    DROP TYPE cvl_id;
    """