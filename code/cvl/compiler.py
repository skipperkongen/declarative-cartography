"""
The compiler uses algorithms in framework.algorithms together with engine specific code generators
"""

import sys

import cvl.framework.generalize as algorithms
import cvl.engines


class CvlCompiler(object):
    """Compiler that turns CVL into transaction code"""
    def __init__(self):
        super(CvlCompiler, self).__init__()

    def compile(self, query, solver='heuristic', target='postgres', algorithm='bottomup', **options):

        if target == 'postgres':
            code_generator = cvl.engines.postgres.CodeGenerator(query, solver, **options)
        else:
            raise NotImplementedError("target not implemented: %s" % str(target))

        if algorithm == 'bottomup':
            return algorithms.BottomUp().get_code(query.zoomlevels, code_generator)


if __name__ == '__main__':
    print 'try 7k_pt_cells_bound.py in the root directory'





