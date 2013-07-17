#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    dataset = DATASETS['fractal']
    constraint = CONSTRAINTS['A']

    job_name = "xl_fractal_heuristic_A"
    QUERY_DICT['input'] = dataset['input'].format(dataset['size'])
    QUERY_DICT['subject_to'] = constraint
    QUERY_DICT['rank_by'] = dataset['rank_by']
    query = Query(**QUERY_DICT)
    print compiler.compile(
        query,
        solver='heuristic',
        target='postgres',
        log_file='/tmp/cvl.log',
        job_name=job_name,
        analytics=False
    )

