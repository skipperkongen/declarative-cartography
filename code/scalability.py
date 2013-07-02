#!/usr/bin/env python

import os
from os.path import basename

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query


# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    compiler = CvlCompiler()
    for size in range(50000, 500001, 50000):
        job_name = os.path.splitext(basename(__file__))[0]
        query_dict = {
            'zoomlevels': 15,
            'input': '(select * from osm_tourism_points where x_order <= {0:d}) t'.format(size),
            'fid': 'ogc_fid',
            'geometry': 'wkb_geometry',
            'other': ['name'],  # , 'type'],
            'rank_by': 'random()'
        }

        for solver in ['lp', 'heuristic']:
            for constraint in [[('cellbound', 16)] ]: #, [('proximity', 10)]]:
                fname = os.path.splitext(basename(__file__))[0]
                job_name = "{0:s}_{1:d}k_{2:s}{3:d}_{4:s}".format(
                    fname,
                    size / 1000,
                    constraint[0][0],
                    constraint[0][1],
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