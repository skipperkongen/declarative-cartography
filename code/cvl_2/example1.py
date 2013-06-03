#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.query import Query, WILDCARD

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 15,
		'input': 'cph_highway',
		'output': 'cph_highway_output',
		'fid': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': ['type', 'name', 'oneway', 'lanes'],
		'rank_by': '1',
	 	'partition_by' : 'type',
		'merge_partitions': [
			(['motorway','motorway_link'], 'motorways'),
			(['primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','road'], 'big_streets'),
			(['residential','pedestrian','living_street'], 'medimum_streets'),
			(WILDCARD, 'the_rest')
		],
		'subject_to' : [('cellbound', 16)],
		'force_level': [('the_rest', 20)],
		'transform_by': ['simplify','allornothing']
	}
	query = Query(**query_dict)
	comp = CvlCompiler(query)
	print comp.generate_sql()