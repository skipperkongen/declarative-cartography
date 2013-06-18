#!/usr/bin/env python

from cvl.compiler.compiler.cvl.compiler import CvlToSqlCompiler
from cvl.compiler.compiler.cvl.query import Query

# ran in 500251 ms = ~8 minutes, on MacBook Pro Dual Core.

if __name__ == '__main__':
	query_dict = {
		'zoomlevels': 18,
		'input': 'openflights_airports',
		'output': 'openflights_airports_thinned',
		'fid': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': ['airport_id, name', 'city', 'country', 'num_routes'],
		'rank_by': 'num_routes',
		'subject_to' : [('proximity', 10)],
	}
	query = Query( **query_dict )
	comp = CvlToSqlCompiler( export=True, drop_tables=True )
	print comp.bottomup_plan( query )