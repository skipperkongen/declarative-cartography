#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    MAX = 512000
    current_size = 4000

    while current_size < MAX:
        for ds_name in ['usriversandstreams', 'fractal']:
            dataset = DATASETS[ds_name]
            for cn_name in ['A', 'B']:
                constraint = CONSTRAINTS[cn_name]
                for solver in ['heuristic']:
                    if dataset['size'] >= current_size / 2.0:
                        job_name = "scala_{0:s}_{1:d}_{2:s}_{3:s}".format(
                            ds_name,
                            current_size,
                            constraint[0][0],
                            solver
                        )
                        QUERY_DICT['input'] = dataset['input'].format(current_size)
                        QUERY_DICT['subject_to'] = constraint
                        QUERY_DICT['rank_by'] = dataset['rank_by']
                        query = Query(**QUERY_DICT)
                        print compiler.compile(
                            query,
                            solver=solver,
                            target='postgres',
                            log_file='/tmp/cvl.log',
                            job_name=job_name,
                            analytics=False
                        )
        current_size *= 2
