#!/usr/bin/env python

__author__ = 'kostas'
from optparse import OptionParser
from cvltrace import TraceReader

import sys

if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph",
                      help="Type of graph to produce: stack")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_usage()
        sys.exit(1)

    tr = TraceReader(args[0])
    traces = tr.get_traces()
    for trace in traces:
        print 'Heppa!'


