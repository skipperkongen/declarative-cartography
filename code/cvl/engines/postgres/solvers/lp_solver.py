__author__ = 'kostas'


_SELECT_CONFLICTS = \
    """
    SELECT
        conflict_id,
        array_agg(record_id) as record_ids,
        array_agg(record_rank) as record_ranks,
        (SELECT min_hits FROM {conflict_table} WHERE conflict_id = conflict_id LIMIT 1)
    FROM
        {conflict_table}
    GROUP BY
        conflict_id;
  """

INSTALL = \
    """
    CREATE OR REPLACE FUNCTION CVL_LPSolver(conflict_table text, lowerbound boolean) RETURNS SETOF bigint AS $$
        import cvxopt
        from math import ceil, floor
        from cvxopt import matrix, spmatrix, sparse, solvers

        sql = _SELECT_CONFLICTS.format(conflict_table=conflict_table)
        conflicts = plpy.execute(sql)

        # make list of variables
        variables = set()
        RID = 0
        RANK = 1
        for c in conflicts:
            variables = variables.union(zip(c['record_ids], c['record_ranks]))
        variables = list(variables)

        # create index of variables
        vindex = {}
        for i, var in enumerate(variables):
            vindex[var[RID]] = i

        # b: non-neg, less-than-one, min_hits
        b = matrix([-1.0] * len(variables) + [1.0] * len(variables) + [c['min_hits'] for c in conflicts])

        # c: ranks
        c = matrix([var[RANK] for var in variables])

        # A:
        non_neg = spmatrix(-1.0, len(variables), len(variables))
        less_than_one = spmatrix(1.0, range(len(variables)), range(len(variables)))
        I = []
        J = []
        for i, c in enumerate(conflicts):
            for v in c['record_ids']:
                I.append(i)
                J.append(vindex[v])
        csets = spmatrix(1.0, I, J)

        A = sparse([non_neg, less_than_one, csets])

        solvers.options['show_progress'] = False
        sol = solvers.lp( c, A, b)

        EPSILON = 0.00001
        if lowerbound:
            snap = lambda x: (1.0 if x > (1.0 - EPSILON) else 0.0)
        else:
            snap = lambda x: (1.0 if x > EPSILON else 0.0)

        if sol['status'] == 'optimal':
            for i, val in enumerate(sol['x']):
                if snap(val) == 1.0
                    yield variables[i][RID]
    $$ LANGUAGE plpythonu;
    """

SOLVE = \
    """
    SELECT * FROM CVL_LPSolver('_conflicts');
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_LPSolver(text, boolean);
    """