#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    QUERY_DICT = {
        'input': 'openflights_airports',
        'output': 'openfligts_airports_thinned',
        'subject_to': [('proximity', 15),('cellbound', 16)],
        'rank_by': 'num_routes',
        'zoomlevels': 18,
        'fid': 'airport_id',
        'geometry': 'wkb_geometry'
    }

    query = Query(**QUERY_DICT)
    print compiler.compile(
        query,
        solver='heuristic',
        target='postgres',
        log_file='/tmp/cvl.log',
        job_name='demo_airports',
        analytics=False
    )

