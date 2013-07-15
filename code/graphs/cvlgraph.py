#!/usr/bin/env python
from __future__ import with_statement

from optparse import OptionParser
from cvltrace import TraceReader

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as font_manager

import sys
import os
import pdb
import re
from datetime import timedelta

__author__ = 'kostas'


class Stack(object):

    def __init__(self, trace):
        self.trace = trace

    def write_out(self):
        width = .8
        zoom_levels = list(reversed(range(len(trace.levels))))
        dtype = [('tasks', 'S16')] + [('', np.float32)]*len(zoom_levels)

        initialize = ['Initialize']
        find_c = ['Find conflicts']
        resolve_c = ['Resolve conflicts']
        finalize = ['Finalize']
        for level in trace.levels:
            initialize.append(level['timing']['initialized_level'].total_seconds())
            find_c.append(level['timing']['found_conflicts'].total_seconds())
            resolve_c.append(level['timing']['resolved_conflicts'].total_seconds())
            finalize.append(level['timing']['finalized_level'].total_seconds())

        y = np.array([
            tuple(initialize),
            tuple(find_c),
            tuple(resolve_c),
            tuple(finalize)
            ],dtype=dtype)
        print y
        y = y.view(np.dtype([('tasks','S16'), ('data', np.float32, len(zoom_levels))]))
        data = y['data']
        tasks = y['tasks']
        bottom = np.zeros(len(zoom_levels))
        for i in range(len(data)):
            bt = plt.bar(range(len(data[i])), data[i], width=width,
                         color=cm.hsv(32*i), label=tasks[i],
                         bottom=bottom)
            bottom += data[i]
        plt.xticks(np.arange(len(zoom_levels)) + width/2,
                   [int(zoom) for zoom in zoom_levels])
        plt.xlabel('Zoom')
        plt.ylabel('Runtime (seconds)')
        plt.title('Performance breakdown')
        plt.legend(loc='upper left',
                   prop=font_manager.FontProperties(size=7))
        #plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))

        jobname = re.sub(r'[\[\]]', '', trace.name)
        filename = os.path.join(output_dir, "{0:s}.png".format(jobname))
        print "Writing figure to {0:s}".format(filename)
        plt.savefig(filename)
        plt.clf()


if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph", default="print",
                      help="Type of graph to produce: stack(default), scalability")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','..','results','figures')
    output_dir = os.path.realpath(output_dir)

    tr = TraceReader(args[0])
    traces = tr.get_traces()
    for trace in traces:
        if options.graph == 'print':
            solution = sum([level['levelstats']['rank_lost'] for level in trace.levels])
            optimum = sum([level['levelstats']['lp_bound'] for level in trace.levels])
            analysis_time = reduce(lambda x,y: x+y,[level['timing']['levelstats'] for level in trace.levels], timedelta(0))

            print trace.name, \
                ' ' * (53 - len(trace.name)), \
                trace.duration, \
                ' ' * 4, (trace.duration - analysis_time), \
                ' ' * 4, 'opt ratio:', solution / optimum if optimum > 0 else 'unknown'
        elif options.graph == 'stack':
            stack_chart = Stack(trace)
            stack_chart.write_out()







