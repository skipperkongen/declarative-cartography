#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    current_size = 1000

    dataset = DATASETS['usriversandstreams']
    while current_size <= dataset['size']:
        for constraint_name in ['A', 'B']:
            constraint = CONSTRAINTS[constraint_name]
            job_name = "scalalin_usriversandstreams_{0:d}_{1:s}_heuristic".format(
                current_size,
                constraint[0][0],
            )
            QUERY_DICT['input'] = dataset['input'].format(current_size)
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
        current_size *= 2
