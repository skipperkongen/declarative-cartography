#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    query_dict = {
        'zoomlevels': 18,
        'input': 'openflights_airports',
        'output': 'airports_thin_cb',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['airport_id', 'name', 'city', 'country', 'num_routes'],
        'rank_by': 'num_routes + random()',
        'subject_to': [('cellbound', 16)],
    }
    query = Query(**query_dict)
    compiler = CvlCompiler()
    print compiler.compile(query, solver='lpbound', target='postgres', log_file='cvl.log', job_name='ex1_bound')