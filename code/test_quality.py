#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    for solver in SOLVERS:
        for constraint in CONSTRAINTS:
            for dataset in DATASETS[0:4]:
                    job_name = "qual_{0:s}_{1:d}_{2:s}_{3:s}".format(
                        dataset['name'],
                        dataset['size'],
                        " ".join([subconstraint[0] for subconstraint in constraint]),
                        solver
                    )
                    QUERY_DICT['input'] = dataset['input'].format(dataset['size'])
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
