# 1: connect to database (input parameters point to tables)
# 2: read data from conflict tables (one for each zoom)
# 3: build LP from conflict data
# 4: solve LP
# 5: write solution (records to delete for each zoom level) to file as *(z, id)* pairs

from cvxopt import matrix, solvers
import psycopg2
from optparse import OptionParser
import sys
import pdb

def build_models( cursor, table ):
	Z = 1
	models = []
	for z in range(Z):
		record_ids = 	['x1','x2']
		record_ranks = 	[42.0,127.0]
		A = 			matrix([ [-1.0, -1.0, 0.0, 1.0], [1.0, -1.0, -1.0, -2.0] ])
		b = 			matrix([ 1.0, -2.0, 0.0, 4.0 ])
		c = 			matrix([ 2.0, 1.0 ])
		models += [(record_ids, record_ranks, A, b, c, z)]
	return models

def connect_to_db( database_connection_string ):
	try:
		conn = psycopg2.connect( database_connection_string )
	except:
		print "could not connect to db using:", database_connection_string
		sys.exit(1)
	cur = conn.cursor()
	return conn, cur

def build_test_table( conn, cur, test_table_name ):
	cur.execute("CREATE TEMP TABLE IF NOT EXISTS {test_table_name} (z int, conflict_id int, record_id text, record_rank float, min_hits int);".format(test_table_name=test_table_name))
	conn.commit()
	cur.execute("INSERT INTO {test_table_name} VALUES (0, 1, 'fid1', 42.0, 1);".format(test_table_name=test_table_name))
	cur.execute("INSERT INTO {test_table_name} VALUES (0, 1, 'fid2', 127.5, 1);".format(test_table_name=test_table_name))
	cur.execute("INSERT INTO {test_table_name} VALUES (0, 1, 'fid3', 17.5, 1);".format(test_table_name=test_table_name))
	conn.commit()

def main(options, table):
	print "Running LP solver for CVL"
	print "\tConnect:\t",		options.database_connection
	print "\tOutput file:\t",	options.output_file
	print "\tTable name:\t", 	table

	# Build models
	conn, cur = connect_to_db( options.database_connection )
	if options.use_test_table:
		# Using a test table
		build_test_table( conn, cur, table )
	print "Building model..."
	models = build_models( cur, table )
	conn.close()
	
	# Solve models
	results = ["zoomlevel,record_id,solution_value,record_rank"]
	solvers.options['show_progress'] = False
	for record_ids, record_ranks, A, b, c, z in models:
		print "Solving model for zoom-level", z
		sol = solvers.lp(c, A, b)
		variables = zip(record_ids, sol['x'], record_ranks)
		for x in filter(lambda x: x[1]>0, variables):
			print x
			#pdb.set_trace()
			results += ["{z},{variable},{variable_value},{variable_rank}".format(z=z, variable=x[0], variable_value=x[1], variable_rank=x[2])]
	
	#pdb.set_trace()
	print "All models solved..."
	f = open(options.output_file, "w")
	for line in results:
		f.write(str(line)+"\n")
	f.close()
	print "Data written to", options.output_file 


if __name__ == '__main__':
	usage = "usage: %prog [options] table_name"
	parser = OptionParser(usage=usage)
	parser.add_option("-t", "--use-test-table", 
		dest="use_test_table", action="store_true", default=False,
		help="Ignore table argument and build a test table to use")
	parser.add_option("-c", "--database-connection", 
		dest="database_connection", default="host='localhost' user='postgres'  password='postgres' dbname='cvl_paper'",
		help="a database connection string")
	parser.add_option("-o", "--output-file", dest="output_file", default="records_to_delete.txt",
		help="Name of a file to write results to")
	(options, args) = parser.parse_args()

	if options.use_test_table:
		main(options, "cvl_conflicts_test_table")
	else:
		main(options, args[0])