#!/usr/bin/env python

import os
from os.path import basename

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query


# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    compiler = CvlCompiler()
    query_dict = {
        'zoomlevels': 15,
        'input': 'synthetic_points_30m',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['name'],
        'rank_by': 'random()'
    }

    for solver in ['lp', 'heuristic']:
        for constraint in [[('cellbound', 16)], [('proximity', 10)]]:
            fname = os.path.splitext(basename(__file__))[0]
            job_name = "{0:s}_{1:s}_{2:s}".format(
                fname,
                constraint[0][0],
                solver
            )
            query_dict['subject_to'] = constraint
            query = Query(**query_dict)
            print compiler.compile(
                query,
                solver=solver,
                target='postgres',
                log_file='/tmp/cvl.log',
                job_name=job_name
            )