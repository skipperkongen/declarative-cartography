#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

import os
from os.path import basename

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    job_name = os.path.splitext(basename(__file__))[0]
    query_dict = {
        'zoomlevels': 18,
        'input': 'openflights_airports',
        'output': 'openflights_airports_thin',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['airport_id', 'name', 'city', 'country', 'num_routes'],
        'rank_by': 'num_routes + random()',
        'subject_to': [('cellbound', 16)],
    }
    query = Query(**query_dict)
    compiler = CvlCompiler()
    print compiler.compile(query, solver='lp', target='postgres', log_file='/tmp/cvl.log', job_name=job_name)