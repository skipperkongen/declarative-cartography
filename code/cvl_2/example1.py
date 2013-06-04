#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.query import Query, WILDCARD

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 20,
		'input': 'cph_highway',
		'output': 'cph_highway_output',
		'fid': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': ['type', 'name', 'oneway', 'lanes'],
		'rank_by': '1',
	 	'partition_by' : 'type',
		'merge_partitions': [
			# http://wiki.openstreetmap.org/wiki/Key:highway
			(['motorway','motorway_link','trunk', 'trunk_link'], 'motorways'),
			(['primary','primary_link','secondary','secondary_link','tertiary','tertiary_link'], 'big_streets'),
			(['residential','pedestrian','living_street','unclassified', 'road'], 'medimum_streets'),
			(['service','track','bus_guideway','raceway','path','footway','cycleway','bridleway','steps','mini_roundabout'], 'small_streets'),
			(WILDCARD, 'the_rest')
		],
		'subject_to' : [('cellbound', 40)],
		'force_level': [('the_rest', 20)],
		'transform_by': ['simplify_once','simplify_carry','allornothing']
	}
	query = Query(**query_dict)
	comp = CvlCompiler(query)
	print comp.generate_sql()