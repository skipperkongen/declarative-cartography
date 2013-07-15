#!/usr/bin/env python

__author__ = 'kostas'
from optparse import OptionParser
from cvltrace import TraceReader

import sys
import pdb
from datetime import timedelta

if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph", default="print",
                      help="Type of graph to produce: stack(default), scalability")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    tr = TraceReader(args[0])
    traces = tr.get_traces()
    for trace in traces:

        if options.graph == 'print':
            solution = sum([level['levelstats']['rank_lost'] for level in trace.levels])
            optimum = sum([level['levelstats']['lp_bound'] for level in trace.levels])
            analysis_time = reduce(lambda x,y: x+y,[level['timing']['levelstats'] for level in trace.levels], timedelta(0))

            print trace.name, \
                ' ' * (52 - len(trace.name)), \
                trace.duration, \
                ' ' * 4, (trace.duration - analysis_time), \
                ' ' * 4, 'opt ratio:', solution / optimum if optimum > 0 else 'unknown'



