#!/usr/bin/env python

from optparse import OptionParser
import sys
import time
import psycopg2
from cvxopt import matrix, spmatrix, sparse

from cvl.framework.convexopt.serializer import Serializer

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

        conflicts = []
        # fetch conflicts from database
        for row in query_buffered(cur, SELECT_CONFLICTS, buffer_size=500, zoom=zoom, table=table):
            conflicts.append({'ids': row[0], 'ranks': row[1], 'min_hits': row[2]})
        num_vars = 42  # CHANGE
        variables = []  # CHANGE

        # generate b (r.h.s.)
        b = matrix([-1.0] * num_vars + [1.0] * num_vars + [c['min_hits'] for c in conflicts])

        # generate c (objective coeffients)
        c = matrix(v['rank'] for v in variables)

        # generate A: non_neg, less_than_one and packing constraints
        non_neg = spmatrix(-1.0, range(num_vars), range(num_vars))
        less_than_one = spmatrix(1.0, range(num_vars), range(num_vars))
        packing = matrix()  # CHANGE
        A = sparse([non_neg, less_than_one, packing])  # stack blocks (sub-matrices) on top of each other

        instances += [dict(A=A, b=b, c=c, variables=variables, zoom=zoom)]
        print " -", ((time.clock() - t0) * 1000), "ms"
    return instances


def connect_to_db(database_connection_string):
    try:
        conn = psycopg2.connect(database_connection_string)
    except Exception, e:
        print "could not connect to db:", str(e)
        sys.exit(1)
    cur = conn.cursor()
    return conn, cur


def build_test_table(conn, cur, table):
    cur.execute(
        """CREATE TEMP TABLE IF NOT EXISTS {table} (
            zoom int, conflict_id int, record_id text, record_rank float, min_hits int
        );""".format(table=table))
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