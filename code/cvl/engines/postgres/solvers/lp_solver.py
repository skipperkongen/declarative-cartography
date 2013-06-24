__author__ = 'kostas'

INSTALL = \
    """
    CREATE OR REPLACE FUNCTION CVL_LPSolver(conflict_table text) RETURNS SETOF bigint AS $$
        import sys
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
    DROP FUNCTION CVL_LPSolver(text);
    """