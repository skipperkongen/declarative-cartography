#!/usr/bin/env python

from optparse import OptionParser
import sys
import time
import psycopg2
from cvxopt import spmatrix, sparse

from serializer import Serializer

SELECT_CONFLICTS = """
SELECT
  array_agg(record_id) as record_ids,
  array_agg(record_rank) as record_ranks,
  (SELECT min_hits FROM {table} where zoom = {zoom} and conflict_id = conflict_id LIMIT 1)
FROM
  {table}
WHERE
  zoom = {zoom}
GROUP BY
  conflict_id;"""

SELECT_COUNT_LEVELS = """
SELECT max(zoom) FROM {table};"""


def query_all(cur, sql, **fields):
    try:
        cur.execute(sql.format(**fields))
        return cur.fetchall()
    except Exception, e:
        print "[ERROR] error querying table:", str(e)
        sys.exit(1)


def query_buffered(cur, sql, buffer_size=1000, **fields):
    cur.execute(sql.format(**fields))
    rows = cur.fetchmany(buffer_size)
    while rows:
        for row in rows:
            yield row
        rows = cur.fetchmany(buffer_size)


def build_instances(cur, table):
    # find number of zoom-levels
    Z = int(query_all(cur, sql=SELECT_COUNT_LEVELS, table=table)[0][0]) + 1

    instances = []
    # build one instance for each zoom-level
    for zoom in range(Z):
        print "building LP instance for level", zoom
        t0 = time.clock()
        variables_set = set()
        conflicts_list = []
        # fetch conflicts from database
        for conflict in query_buffered(cur, SELECT_CONFLICTS, buffer_size=500, zoom=zoom, table=table):
            conflicts_list.append({'ids': set(conflict[0]), 'min_hits': conflict[2]})
            variables_in_conflict = set(zip(conflict[0], conflict[1]))
            variables_set = variables_set.union(variables_in_conflict)  # extend variable set

        variables_list = [{'id': fid, 'rank': rank} for fid, rank in variables_set]
        A, b_list, c_list = [], [], []
        # generate A and c one column at a time, variables (cols) in outer loop, conflicts (rows) in inner loop
        for i, var in enumerate(variables_list):
            # create c vector
            c_list.append(var['rank'])  # coefficients
            # create A matrix
            A_col = []
            for j in range(len(variables_list)):
                # non-negativity and less than one constraints
                A_col.append(-float(i == j))  # non-neg
                A_col.append(float(i == j))  # less than one
            for cn in conflicts_list:
                # hitting set constraints
                A_col.append(-float(var['id'] in cn['ids']))
            A.append(A_col)
            # create b vector, looping over conflicts
        for i in range(len(variables_list)):
            # non-negativity and less than one RHS
            b_list.append(0.0)  # non-neg
            b_list.append(1.0)  # less than one
        for cn in conflicts_list:
            # hitting set RHS
            b_list.append(-float(cn['min_hits']))
        record_ids = map(lambda x: x['id'], variables_list)
        record_ranks = map(lambda x: x['rank'], variables_list)
        # record_ranks and c_list are the same
        instances += [dict(record_ids=record_ids, record_ranks=record_ranks, A=A, b=b_list, c=c_list, zoom=zoom)]
        print " - A matrix (cols,rows): %d x %d" % (len(c_list), len(b_list))
        print " -", ((time.clock() - t0) * 1000), "ms"
    return instances


def connect_to_db(database_connection_string):
    try:
        conn = psycopg2.connect(database_connection_string)
    except:
        print "could not connect to db using:", database_connection_string
        sys.exit(1)
    cur = conn.cursor()
    return conn, cur


def build_test_table(conn, cur, table):
    cur.execute(
        "CREATE TEMP TABLE IF NOT EXISTS {table} (zoom int, conflict_id int, record_id text, record_rank float, min_hits int);".format(
            table=table))
    conn.commit()
    cur.execute("INSERT INTO {table} VALUES (0, 1, 'fid1', 42.0, 1);".format(table=table))
    cur.execute("INSERT INTO {table} VALUES (0, 1, 'fid2', 127.5, 1);".format(table=table))
    cur.execute("INSERT INTO {table} VALUES (0, 2, 'fid1', 42.0, 1);".format(table=table))
    cur.execute("INSERT INTO {table} VALUES (0, 2, 'fid3', 27.1, 1);".format(table=table))
    cur.execute("INSERT INTO {table} VALUES (1, 3, 'fid4', 17.5, 1);".format(table=table))
    cur.execute("INSERT INTO {table} VALUES (1, 3, 'fid5', 32.2, 1);".format(table=table))
    conn.commit()


def main(options, table):
    # connect to database
    conn, cur = connect_to_db(options.database_connection)
    if options.use_test_table:
        # Use a test table
        build_test_table(conn, cur, table)

    # build instances
    instances = build_instances(cur, table)
    cur.close()
    conn.close()

    # write instances
    Serializer().serialize(instances, options.output_file)

    print "Solution written to", options.output_file


if __name__ == '__main__':
    usage = "usage: %prog [options] table_name"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--use-test-table",
                      dest="use_test_table", action="store_true", default=False,
                      help="Ignore table argument and build a test table to use")
    parser.add_option("-c", "--database-connection",
                      dest="database_connection",
                      default="host='localhost' user='postgres'  password='postgres' dbname='cvl_paper'",
                      help="a database connection string")
    parser.add_option("-o", "--output-file", dest="output_file", default="hittingset.lp",
                      help="Name of a file to write results to")
    (options, args) = parser.parse_args()

    if options.use_test_table:
        main(options, "cvl_conflicts_test_table")
    else:
        main(options, args[0])