#!/usr/bin/env python

from optparse import OptionParser
import time
import pprint
import os

from cvl.framework.convexopt.serializer import Serializer


def main(options, input_file):
	
	os.system("banner X")
	print "Deserializing LP instances"
	t0 = time.clock()
	instances = Serializer().deserialize( input_file )	
	print " -",((time.clock()-t0) * 1000),"ms"
	
	pp = pprint.PrettyPrinter(indent=2,depth=3)
	for instance in instances:
		if instance['zoom'] > options.max_zoom: continue
		print "-"*42
		print "Zoom-level:", instance['zoom']
		print "-"*42
		print "c:"
		print( map(lambda x: round(x,2), instance['c']) )
		print "A:"
		for row in instance['A']:
			print( row )
		print "b:"
		print( instance['b'] )

if __name__ == '__main__':
	usage = "usage: %prog input_file"
	parser = OptionParser(usage=usage)
	parser.add_option("-m", "--max-zoom", type="int", dest="max_zoom", default=0,
		help="Name of a file to write results to")
	(options, args) = parser.parse_args()
	main(options, args[0])