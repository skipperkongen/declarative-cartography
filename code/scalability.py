#!/usr/bin/env python

import os
from os.path import basename

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query


# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    compiler = CvlCompiler()

    MAX = 1024000

    input_tourism = '(select * from osm_tourism_points where x_order <= {0:d}) t'
    input_waterways = '(select * from osm_waterways_linestrings where x_order <= {0:d}) t'
    rank_tourism = 'random()'
    rank_waterways = 'st_length(wkb_geometry)'

    query_dict = {
        'zoomlevels': 15,
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry'
    }

    solvers = ['lp', 'heuristic']
    constraints = [[('cellbound', 16)], [('proximity', 10)]]
    datasets = [
        {'name': 'tourism', 'input': input_tourism, 'rank_by': rank_tourism, 'size': 512000},
        {'name': 'waterways', 'input': input_waterways, 'rank_by': rank_waterways, 'size': 1024000}
    ]

    current_size = 4000

    while current_size <= MAX:
        for solver in solvers:
            for constraint in constraints:
                for dataset in datasets:
                    if current_size <= dataset['size']:
                        job_name = "{0:s}_{1:d}_{2:s}_{3:s}".format(
                            dataset['name'],
                            current_size,
                            constraint[0][0],
                            solver
                        )
                        query_dict['input'] = dataset['input'].format(current_size)
                        query_dict['subject_to'] = constraint
                        query_dict['rank_by'] = dataset['rank_by']
                        query = Query(**query_dict)
                        print compiler.compile(
                            query,
                            solver=solver,
                            target='postgres',
                            log_file='/tmp/cvl.log',
                            job_name=job_name
                        )
        current_size *= 2
