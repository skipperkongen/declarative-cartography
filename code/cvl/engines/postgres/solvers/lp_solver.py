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
        variables = set()
        for c in conflicts:
            vars = zip(c['record_ids], c['record_ranks])
            variables = variables.union(vars)

        variables = list(variables)

        # b: non-neg, less-than-one, min_hits
        b = matrix([-1.0] * len(variables) + [1.0] * len(variables) + [c['min_hits'] for c in conflicts])

        # c: ranks
        c = matrix(v[1] for v in variables)

        # A:
        var_dict = dict(
            [
                (x[0], {'pos':i, 'rank: x[1]}) for i,x in enumerate(variables)
            ]
        )
        non_neg = spmatrix(-1.0, range(num_vars), range(num_vars))
        less_than_one = spmatrix(1.0, range(num_vars), range(num_vars))
        A = sparse([non_neg, less_than_one, ])
        # TODO: ...continue with model building, above

        solvers.options['show_progress'] = False
        sol = solvers.lp( c, A, b)

        for i in range(42):
            yield i
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