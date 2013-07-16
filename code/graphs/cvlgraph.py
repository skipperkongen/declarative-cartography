#!/usr/bin/env python
from __future__ import with_statement

from optparse import OptionParser
from cvltrace import TraceReader

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.font_manager as font_manager

import sys
import os
import re
from datetime import timedelta

__author__ = 'kostas'

class QualAccum(object):

    def __init__(self, trace):
        self.trace = trace

    def write_out(self):
        num_levels = len(self.trace.levels)

        current_rank = self.trace.inputstats['total_rank']
        x = []
        opt = []
        actual = []
        for level in self.trace.levels:
            x.append(level['zoom'])
            opt.append(current_rank - level['levelstats']['lp_bound'])
            actual.append(level['levelstats']['rank_remaining'])
            current_rank = level['levelstats']['rank_remaining']

        plt.plot(x, opt, label='Lower bound')
        plt.plot(x, actual, label='Solution')
        #plt.xticks(np.arange(len(zoom_levels)) + (width/2),
        #           [int(zoom) for zoom in zoom_levels])
        plt.xlabel('Zoom')
        plt.ylabel('Weight remaining')
        if len(self.trace.constraints) == 30:
            constr = 'AB'
        elif self.trace.constraints.startswith('cell'):
            constr = 'A'
        else:
            constr = 'B'
        plt.title('{0:s}: {1:s} + {2:s}'.format(
            self.trace.input_table,
            self.trace.solver,
            constr))
        plt.legend(loc='upper left',
                   prop=font_manager.FontProperties(size=10))
        #plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))

        filename = os.path.join(output_dir, "prelim_qual_{0:s}_{1:s}_{2:s}.png".format(
            #re.sub(r'[\[\]]', '', trace.name)))
            self.trace.input_table,
            self.trace.solver,
            constr))
        print "Writing figure to {0:s}".format(filename)
        plt.savefig(filename)
        plt.clf()




class Stack(object):

    def __init__(self, trace):
        self.trace = trace

    def write_out(self):
        width = .8
        zoom_levels = list(reversed(range(len(trace.levels))))
        dtype = [('tasks', 'S16')] + [('', np.float32)]*len(zoom_levels)

        initialize = ['Initialize']
        find_c = ['Find conflicts']
        resolve_c = ['Solve']
        finalize = ['Finalize']
        for level in self.trace.levels:
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
        y = y.view(np.dtype([('tasks','S16'), ('data', np.float32, len(zoom_levels))]))
        data = y['data']
        tasks = y['tasks']
        bottom = np.zeros(len(zoom_levels))
        for i in range(len(data)):
            bt = plt.bar(range(len(data[i])), data[i], width=width,
                         color=cm.hsv(24*i), label=tasks[i],
                         bottom=bottom)
            bottom += data[i]
        plt.xticks(np.arange(len(zoom_levels)) + (width/2),
                   [int(zoom) for zoom in zoom_levels])
        plt.xlabel('Zoom')
        plt.ylabel('Runtime (seconds)')
        if len(self.trace.constraints) == 30:
            constr = 'AB'
        elif self.trace.constraints.startswith('cell'):
            constr = 'A'
        else:
            constr = 'B'
        plt.title('{0:s}: {1:s} + {2:s}'.format(
            self.trace.input_table,
            self.trace.solver,
            constr))
        plt.legend(loc='upper right',
                   prop=font_manager.FontProperties(size=10))
        #plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))

        filename = os.path.join(output_dir, "prelim_{0:s}_{1:s}_{2:s}.png".format(
            #re.sub(r'[\[\]]', '', trace.name)))
            self.trace.input_table,
            self.trace.solver,
            constr))
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

    if options.graph == 'print':
        for trace in tr.get_traces():
            solution = sum([level['levelstats']['rank_lost'] for level in trace.levels])
            optimum = sum([level['levelstats']['lp_bound'] for level in trace.levels])
            analysis_time = reduce(lambda x,y: x+y,[level['timing']['levelstats'] for level in trace.levels], timedelta(0))

            print trace.name, \
                ' ' * (53 - len(trace.name)), \
                trace.duration, \
                ' ' * 4, (trace.duration - analysis_time), \
                ' ' * 4, 'opt ratio:', solution / optimum if optimum > 0 else 'unknown'

    elif options.graph == 'stack':
        for trace in tr.get_traces():
            chart = Stack(trace)
            chart.write_out()

    elif options.graph == 'qualaccum':
        for trace in tr.get_traces():
            chart = QualAccum(trace)
            chart.write_out()
    else:
        print 'unknown chart type'








