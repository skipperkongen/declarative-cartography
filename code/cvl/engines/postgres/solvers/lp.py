__author__ = 'kostas'

INSTALL = \
    """
    CREATE OR REPLACE FUNCTION CVL_GreedyLP(conflict_table text) RETURNS SETOF lp_result AS $$

        sql = "SELECT * FROM CVL_LP('{0:s}');".format(conflict_table)
        rows = plpy.execute(sql)
        EPSILON = 0.00001
        snap = lambda x: (1.0 if x > EPSILON else 0.0)

        for row in rows:
                if snap(row['lp_value']) == 1.0:
                    yield row

    $$ LANGUAGE plpythonu VOLATILE;
    """

SOLVE = \
    """
    SELECT cvl_id FROM CVL_GreedyLP('_conflicts')
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_GreedyLP(text);
    """