#!/usr/bin/env python
__author__ = 'kostas'

from test_util import *
from cvl.compiler import CvlCompiler
from cvl.framework.query import Query

if __name__ == '__main__':
    compiler = CvlCompiler()

    for dataset in DATASETS[0:4]:
        for constraint in CONSTRAINTS:
            for solver in SOLVERS:
                    job_name = "basic_{0:s}_{1:d}_{2:s}_{3:s}".format(
                        dataset['name'],
                        dataset['size'],
                        '-'.join(map(lambda x: x[0], constraint)),
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
