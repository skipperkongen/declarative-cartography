#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.query import Query, WILDCARD

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 16,
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
		'subject_to' : [('avgdensity', 0.3)],
		'transform_by': ['simplify_once']
	}
	query = Query(**query_dict)
	comp = CvlCompiler(query)
	print comp.generate_sql()