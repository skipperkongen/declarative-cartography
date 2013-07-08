#!/usr/bin/env python

from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

import os
from os.path import basename

# runs in ~1 minute, on MacBook Pro Dual Core.

if __name__ == '__main__':
    compiler = CvlCompiler()
    query_dict = {
        'zoomlevels': 15,
        'input': 'dai_polygons',
        'fid': 'ogc_fid',
        'geometry': 'wkb_geometry',
        'other': ['temanavn'],
        #'other': ['airport_id', 'name', 'city', 'country', 'num_routes'],
        'rank_by': 'st_area(wkb_geometry)/1000000'
    }
    for solver in ['lp', 'heuristic']:
        for constraint in [[('proximity', 10)], [('cellbound', 16)]]:
            fname = os.path.splitext(basename(__file__))[0]
            job_name = "{0:s}_{1:s}{2:d}_{3:s}".format(fname, constraint[0][0], constraint[0][1], solver)
            query_dict['subject_to'] = constraint
            query = Query(**query_dict)
            print compiler.compile(query, solver=solver, target='postgres', log_file='/tmp/cvl.log', job_name=job_name)
