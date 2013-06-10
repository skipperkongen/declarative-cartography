# 4: solve LP
# 5: write solution (records to delete for each zoom level) to file as *(z, id)* pairs

from cvxopt import matrix, solvers
from optparse import OptionParser
import ConfigParser
import sys
import pdb
from math import floor
from serializer import Serializer

EPSILON = 0.0001

snap = lambda x: math.ceil(x) if abs(x - round(x)) > EPSILON else round(x)

def main(options, input_file):

	instances = Serializer().deserialize( input_file )	
	
	# Solve instances
	results = ["zoomlevel,record_id,solution_value,record_rank"]
	solvers.options['show_progress'] = False
	for instance in instances:
		A = matrix(instance['A'])
		b = matrix(instance['b'])
		c = matrix(instance['c'])
		z = instance['z']
		record_ids = instance['record_ids']
		record_ranks = instance['record_ranks']		
		sol = solvers.lp( c, A, b)
		variables = zip( record_ids, sol['x'], record_ranks )
		for x in filter(lambda x: snap(x[1])>0, variables):
			results += ["{z},{variable},{variable_value},{variable_rank}".format(z=z, variable=x[0], variable_value=snap(x[1]), variable_rank=x[2])]
	
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