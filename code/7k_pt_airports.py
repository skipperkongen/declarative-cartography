#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

import os
from os.path import basename

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    compiler = CvlCompiler()
    query_dict = {
        'zoomlevels': 18,
        'input': 'openflights_airports',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['airport_id', 'name', 'city', 'country', 'num_routes'],
        'rank_by': 'num_routes + random()',
        'subject_to': [('cellbound', 16)],
    }
    for solver in ['bound', 'lp', 'heuristic']:
        for constraint in [[('cellbound', 16)], [('proximity', 10)]]:
            fname = os.path.splitext(basename(__file__))[0]
            job_name = "{0:s}_{1:s}{2:d}_{3:s}".format(fname, constraint[0][0], constraint[0][1], solver)
            query_dict['subject_to'] = constraint
            query = Query(**query_dict)
            print compiler.compile(query, solver=solver, target='postgres', log_file='/tmp/cvl.log', job_name=job_name)
