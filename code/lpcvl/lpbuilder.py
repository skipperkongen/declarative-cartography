#!/usr/bin/env python

import psycopg2
from optparse import OptionParser
import sys
import pdb
from math import floor
import ConfigParser
from serializer import Serializer
import time

BUFFER_SIZE = 1000

def build_instances( cur, table ):
	# find number of zoom-levels
	try:
		cur.execute("SELECT max(zoom) FROM {table};".format(table=table))
	except Exception, e:
		print "[ERROR] error querying table:", str(e)
		sys.exit(1)
	Z = int(cur.fetchall()[0][0]) + 1 # zoom-levels zero-indexed
		
	# build model for each zoom-level
	models = []
	for zoom in range(Z):
		if zoom > 3:
			print "quitting, instances are becoming too large"
			break
		print "building LP instance for level", zoom
		t0 = time.clock()
		_variables = set()
		conflicts = []
		# get data for A and c
		cur.execute("""
		SELECT 
			conflict_id,
			array_agg(record_id) as record_ids, 
			array_agg(record_rank) as record_ranks, 
			(SELECT min_hits FROM {table} where conflict_id=conflict_id LIMIT 1)
		FROM 
			{table}
		WHERE zoom = {zoom}
		GROUP BY
			conflict_id;""".format(zoom=zoom,table=table))
		rows = cur.fetchmany(BUFFER_SIZE)
		# Create A, b, c
		while rows:
			for row in rows:
				# zoom 0 : (1, ['fid1', 'fid2'], [42.0, 127.5], 1)
				# zoom 1 : (1, ['fid3', 'fid4'], [17.5, 127.5], 1)
				conflict_id 	= row[0]
				record_ids 		= row[1]
				record_ranks 	= row[2]
				min_hits 		= row[3]
				var_subset = set( zip(record_ids, record_ranks) )
				_variables = _variables.union( var_subset ) # extend variable set
				conflicts.append( {'ids': set(record_ids), 'min_hits': min_hits} )
			rows = cur.fetchmany(BUFFER_SIZE)
		
		variables = [{'id':fid, 'rank':rank} for fid, rank in _variables]
		A, b, c = [], [], []
		# generate A and c one column at a time, variables (cols) in outer loop, conflicts (rows) in inner loop
		for i, var in enumerate(variables):
			# create c vector
			c.append(var['rank']) # coefficients
			# create A matrix
			A_col = []
			for j in range(len(variables)):
				# non-negativity and less than one constraints
				A_col.append( -float(i==j)) # non-neg
				A_col.append(  float(i==j)) # less than one
			for cn in conflicts:
				# hitting set constraints
				A_col.append( -float(var['id'] in cn['ids']) )
			A.append( A_col )
		# create b vector, looping over conflicts
		for i in range(len(variables)):
			# non-negativity and less than one RHS
			b.append( 0.0 ) # non-neg
			b.append( 1.0 ) # less than one
		for cn in conflicts:
			# hitting set RHS
			b.append( -float(cn['min_hits']) )
		record_ids 		= map(lambda x: x['id'], variables)
		record_ranks 	= map(lambda x: x['rank'], variables)
		models += [{
			'record_ids': record_ids, 
			'record_ranks': record_ranks, 
			'A': A, 
			'b': b, 
			'c': c, 
			'zoom': zoom
		}]
		print " - A matrix (cols,rows): %d x %d" % (len(c), len(b))
		print " -",((time.clock()-t0) * 1000),"ms"
	return models

def connect_to_db( database_connection_string ):
	try:
		conn = psycopg2.connect( database_connection_string )
	except:
		print "could not connect to db using:", database_connection_string
		sys.exit(1)
	cur = conn.cursor()
	return conn, cur

def build_test_table( conn, cur, table ):
	cur.execute("CREATE TEMP TABLE IF NOT EXISTS {table} (zoom int, conflict_id int, record_id text, record_rank float, min_hits int);".format(table=table))
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
	conn, cur = connect_to_db( options.database_connection )
	if options.use_test_table:
		# Use a test table
		build_test_table( conn, cur, table )

	# build instances
	instances = build_instances( cur, table )
	cur.close()
	conn.close()

	# write instances
	Serializer().serialize( instances, options.output_file)
		
	print "Solution written to", options.output_file 

if __name__ == '__main__':
	usage = "usage: %prog [options] table_name"
	parser = OptionParser(usage=usage)
	parser.add_option("-t", "--use-test-table", 
		dest="use_test_table", action="store_true", default=False,
		help="Ignore table argument and build a test table to use")
	parser.add_option("-c", "--database-connection", 
		dest="database_connection", default="host='localhost' user='postgres'  password='postgres' dbname='cvl_paper'",
		help="a database connection string")
	parser.add_option("-o", "--output-file", dest="output_file", default="hittingset.lp",
		help="Name of a file to write results to")
	(options, args) = parser.parse_args()

	if options.use_test_table:
		main(options, "cvl_conflicts_test_table")
	else:
		main(options, args[0])