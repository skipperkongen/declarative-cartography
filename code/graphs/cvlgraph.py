#!/usr/bin/env python

__author__ = 'kostas'
from optparse import OptionParser
from cvltrace import TraceReader

import sys
import pdb

if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph", default="stack",
                      help="Type of graph to produce: stack(default), scalability")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    tr = TraceReader(args[0])
    traces = tr.get_traces()
    for trace in traces:
        solution = sum([level['stats']['rank_lost'] for level in trace.levels])
        optimum = sum([level['stats']['lp_bound'] for level in trace.levels])

        print trace.name, \
            ' ' * (45 - len(trace.name)), \
            trace.duration, \
            '\topt ratio:', \
            solution / optimum if optimum > 0 else 'unknown'



