#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    dataset = DATASETS[0]
    solver = SOLVERS[0]
    constraint = CONSTRAINTS[0]

    job_name = "airports"
    QUERY_DICT['input'] = dataset['input'].format(dataset['size'])
    QUERY_DICT['subject_to'] = constraint
    QUERY_DICT['rank_by'] = dataset['rank_by']
    query = Query(**QUERY_DICT)
    print compiler.compile(
        query,
        solver=SOLVERS[0],
        target='postgres',
        log_file='/tmp/cvl.log',
        job_name=job_name,
        analytics=False
    )

