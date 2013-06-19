"""
The compiler uses algorithms in framework.algorithms together with engine specific code generators
"""

import sys

import cvl.framework.algorithms as algorithms
import cvl.engines


class CvlCompiler(object):
    """Compiler that turns CVL into transaction code"""
    def __init__(self):
        super(CvlCompiler, self).__init__()

    def compile(self, cvl_query, target='postgres', algorithm='bottomup', **kwargs):

        if target == 'postgres':
            code_generator = cvl.engines.postgres.CodeGenerator(**kwargs)
        else:
            raise NotImplementedError("target not implemented: %s" % str(target))

        if algorithm == 'bottomup':
            return algorithms.BottomUp().get_code(cvl_query, code_generator)


if __name__ == '__main__':
    print 'try example1.py in the root directory'





