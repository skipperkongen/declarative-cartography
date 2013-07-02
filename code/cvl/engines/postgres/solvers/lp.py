__author__ = 'kostas'

INSTALL = \
    """
    CREATE TYPE cvl_id AS (
      cvl_id bigint
    );

    CREATE OR REPLACE FUNCTION CVL_LPSolver(conflict_table text) RETURNS SETOF cvl_id AS $$
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

        EPSILON = 0.00001
        snap = lambda x: (1.0 if x > EPSILON else 0.0)

        if sol['status'] == 'optimal':
            for i, val in enumerate(sol['x']):
                if snap(val) == 1.0:
                    yield {'cvl_id': i_to_var[i]}
        else:
            plpy.error("Infeasible LP instance detected by solver!")

    $$ LANGUAGE plpythonu;
    """

SOLVE = \
    """
    SELECT cvl_id FROM CVL_LPSolver('_conflicts')
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_LPSolver(text);
    DROP TYPE cvl_id;
    """