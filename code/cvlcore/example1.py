#!/usr/bin/env python

from cvl.compiler import CvlToSqlCompiler
from cvl.query import Query, WILDCARD

# ran in 500251 ms = ~8 minutes, on MacBook Pro Dual Core.

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 18,
		'input': 'cph_highway',
		'output': 'cph_highway_output',
		'fid': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': ['type', 'name', 'oneway', 'lanes'],
		'rank_by': '1',
	 	'partition_by' : 'type',
		'merge_partitions': [
			(['motorway','motorway_link','motorway_junction','trunk', 'trunk_link'], 'motorways'),
			(['primary','primary_link','secondary','secondary_link','tertiary','tertiary_link'], 'big_streets'),
			(['residential','pedestrian','living_street','unclassified', 'roundabout','road'], 'medium_streets'),
			(['service','track','bus_guideway','raceway','path','footway','cycleway','bridleway','steps','mini_roundabout'], 'small_streets'),
			(WILDCARD, 'the_rest')],
		'subject_to' : [('cellbound', 800)],
		'force_level': [('the_rest', 15)],
		'transform_by': ['allornothing','simplify_once']
	}
	query = Query( **query_dict )
	comp = CvlToSqlCompiler( export=True, drop_tables=True )
	print comp.bottomup_plan( query )