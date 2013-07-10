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
        for solver in SOLVERS:
            for constraint in CONSTRAINTS:
                for dataset in DATASETS:
                        if dataset['size'] >= current_size / 2.0:
                            job_name = "scal_{0:s}_{1:d}_{2:s}_{3:s}".format(
                                dataset['name'],
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
                                job_name=job_name
                            )
        current_size *= 2

