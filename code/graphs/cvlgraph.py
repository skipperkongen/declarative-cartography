#!/usr/bin/env python
from __future__ import with_statement

from optparse import OptionParser
from cvltrace import TraceReader

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
import matplotlib.font_manager as font_manager

import sys
import os
import re
import pdb
from datetime import timedelta

__author__ = 'kostas'


class Scalability(object):

    def __init__(self, traces):
        self.traces = traces
        self.ds_name = [trace.input_table for trace in traces][0]

    def write_out(self):
        to_label = lambda key: \
            ('SGA' if key[0][0] == 'h' else 'LPGA') + (' + A' if key[1][0] == 'c' else ' + B')

        x_formatter = lambda x, pos: 'foo'
        # series for group by (table, constraint, solver)
        sizes = set()
        series = {}
        for trace in self.traces:
            key = (trace.solver,trace.constraints)
            series.setdefault(key, {})[trace.inputstats['total_recs']] = trace.duration

        for key, serie in series.items():
            sizes = sizes.union([size for size in sorted(serie)])
            x = [size for size in sorted(serie)]
            y = [serie[size].total_seconds() for size in sorted(serie)]
            plt.loglog(x, y, 'o-', label=to_label(key))
        leg = plt.legend(loc='best',fancybox=True)
        leg.get_frame().set_alpha(0.6)
        plt.xlabel('Data size')
        plt.ylabel('Runtime (seconds)')
        filename = os.path.join(output_dir, "scal_{0:s}.png".format(self.ds_name))
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(filename)
        plt.clf()
        print "Writing figure to {0:s}".format(filename)
        #plt.show()


class Stack(object):

    def __init__(self, trace):
        self.trace = trace

    def write_out(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

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
            bt = ax1.bar(range(len(data[i])), data[i], width=width,
                         color=cm.hsv(24*i), label=tasks[i],
                         bottom=bottom)
            bottom += data[i]
        plt.xticks(np.arange(len(zoom_levels)) + (width/2),
                   [int(zoom) for zoom in zoom_levels])
        ax1.set_xlabel('Zoom')
        ax1.set_ylabel('Runtime (seconds)')
        if len(self.trace.constraints) == 30:
            constr = 'AB'
        elif self.trace.constraints.startswith('cell'):
            constr = 'A'
        else:
            constr = 'B'
        #plt.title('{0:s}: {1:s} + {2:s}'.format(
        #    self.trace.input_table,
        #    self.trace.solver,
        #    constr))
        ax2 = ax1.twinx()

        ax2.plot(range(len(zoom_levels)), [level['levelstats']['num_c'] for level in trace.levels], 'o-', linewidth=2,
                 c="black")
        ax2.set_ylabel('conflicts')

        if trace.input_table == 'pnt_7k_airports':
            leg = ax1.legend(loc='upper left', fancybox=True)
        else:
            leg = ax1.legend(loc='upper right',fancybox=True)


        leg.get_frame().set_alpha(0.6)
        #plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))

        filename = os.path.join(output_dir, "prelim_{0:s}_{1:s}_{2:s}.png".format(
            #re.sub(r'[\[\]]', '', trace.name)))
            self.trace.input_table,
            self.trace.solver,
            constr))
        print "Writing figure to {0:s}".format(filename)
        plt.subplots_adjust(wspace=1.4)
        plt.savefig(filename)
        plt.clf()


class OptimalityRatio(object):

    def __init__(self, trace):
        self.solution = 0
        self.lowerbound = 0
        self.numlevels = len(trace.levels)
        for level in trace.levels:
            self.solution += (level['levelstats']['rank_lost'])
            self.lowerbound += (level['levelstats']['lp_bound'])

    def get_lowerbound(self):
        return self.lowerbound

    def get_solution(self):
        return self.solution

    def get_ratio(self):
        return (self.solution / float(self.numlevels)) / (float(self.lowerbound) / self.numlevels)


if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile"
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph", default="print",
                      help="Type of graph to produce: stack(default), scalability")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    matplotlib.rcParams.update({'font.size': 20})

    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','..','results','figures')
    output_dir = os.path.realpath(output_dir)

    tr = TraceReader(args[0])

    if options.graph == 'print':
        for trace in tr.get_traces():
            optratio = OptimalityRatio(trace)
            analysis_time = reduce(lambda x, y: x+y,
                                   [level['timing']['levelstats'] for level in trace.levels],
                                   timedelta(0))

            print trace.name, \
                ' ' * (53 - len(trace.name)), \
                trace.duration, \
                ' ' * 4, (trace.duration - analysis_time), \
                ' ' * 4, 'opt ratio:', optratio.get_ratio() if optratio.lowerbound > 0 else 'unknown'

    elif options.graph == 'print_nostat':
        for trace in tr.get_traces():
            print trace.name, \
                trace.duration

    elif options.graph == 'stack':
        for trace in tr.get_traces():
            chart = Stack(trace)
            chart.write_out()

    elif options.graph == 'scala':
        chart = Scalability(tr.get_traces())
        chart.write_out()
    else:
        print 'unknown chart type'








