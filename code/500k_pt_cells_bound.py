#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

import os
from os.path import basename

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    job_name = os.path.splitext(basename(__file__))[0]
    query_dict = {
        'zoomlevels': 15,
        'input': 'osm_tourism_points',
        'output': 'tourism_thin_prox',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['name', 'type'],
        'rank_by': 'random()',
        'subject_to': [('cellbound', 16)],
    }
    query = Query(**query_dict)
    compiler = CvlCompiler()
    print compiler.compile(query, solver='lpbound', target='postgres', log_file='/tmp/cvl.log', job_name=job_name)