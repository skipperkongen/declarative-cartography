#!/usr/bin/env python

from cvxopt import matrix, solvers
from optparse import OptionParser
import ConfigParser
import sys
import pdb
from math import ceil
from serializer import Serializer
import time

EPSILON = 0.0001

#snap = lambda x: x if abs(x - round(x)) > EPSILON else round(x)
#snap = lambda x: ceil(x) if abs(x - round(x)) > EPSILON else round(x)
snap = lambda x: min(1, ceil(x))
#snap = lambda x: x

def main(options, input_file):

	print "Deserializing LP instances"
	t0 = time.clock()
	instances = Serializer().deserialize( input_file )	
	print " -",((time.clock()-t0) * 1000),"ms"
	
	# Solve instances
	results = ["zoom,record_id,record_rank,lp_value"]
	solvers.options['show_progress'] = False
	for instance in instances:
		A = matrix(instance['A'])
		b = matrix(instance['b'])
		c = matrix(instance['c'])
		zoom = instance['zoom']
		record_ids = instance['record_ids']
		record_ranks = instance['record_ranks']
		print "solving for zoom-level",zoom
		t0 = time.clock()
		sol = solvers.lp( c, A, b)
		print " -",((time.clock()-t0) * 1000),"ms"
		variables = zip( record_ids, sol['x'], record_ranks )
		for x in filter(lambda x: snap(x[1])>0, variables):
			results += ["{zoom},{variable},{variable_rank},{variable_value}".format(zoom=zoom, variable=x[0], variable_value=snap(x[1]), variable_rank=x[2])]
	
	f = open(options.output_file, "w")
	for line in results:
		f.write(str(line)+"\n")
	f.close()
	print "Solution written to", options.output_file 


if __name__ == '__main__':
	usage = "usage: %prog input_file"
	parser = OptionParser(usage=usage)
	parser.add_option("-o", "--output-file", dest="output_file", default="records_to_delete.sol",
		help="Name of a file to write results to")
	(options, args) = parser.parse_args()
	main(options, args[0])