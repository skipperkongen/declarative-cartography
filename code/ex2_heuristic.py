#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    query_dict = {
        'zoomlevels': 18,
        'input': 'osm_tourism_points',
        'output': 'tourism_thin_prox',
        'fid': 'osm_id',
        'geometry': 'wkb_geometry',
        'other': ['name', 'type'],
        'rank_by': 'random()',
        'subject_to': [('proximity', 10)],
    }
    query = Query(**query_dict)
    compiler = CvlCompiler()
    print compiler.compile(query, solver='heuristic', target='postgres', log_file='cvl.log', job_name='example4')