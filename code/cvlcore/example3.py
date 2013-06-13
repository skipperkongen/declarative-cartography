#!/usr/bin/env python

from cvl.compiler import CvlToSqlCompiler
from cvl.query import Query, WILDCARD

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 18,
		'input': 'openflights_airports',
		'output': 'openflights_airports_thinned_cb',
		'fid': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': ['airport_id, name', 'city', 'country', 'num_routes'],
		'rank_by': 'num_routes + random()',
		'subject_to' : [('cellbound', 16)],
	}
	query = Query( **query_dict )
	comp = CvlToSqlCompiler( export=True, drop_tables=True )
	print comp.bottomup_plan( query )