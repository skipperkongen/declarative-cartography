__author__ = 'kostas'

INSTALL = \
    """
    CREATE OR REPLACE FUNCTION CVL_GreedyLP(conflict_table text) RETURNS SETOF lp_result AS $$

        sql = "SELECT * FROM CVL_LP('{0:s}');".format(conflict_table)
        rows = plpy.execute(sql)
        EPSILON = 0.00001
        # find biggest conflict
        f = plpy.execute('select max(count) as f from (select count(*) as count from {0:s} group by conflict_id) t;'.format(
            conflict_table
        ))[0]['f']
        snap = lambda x: (1.0 if x > (1.0/f - EPSILON) else 0.0)

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