
from __future__ import with_statement
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as font_manager
import pdb

__author__ = 'kostas'


def billions(x, pos):
    return '%1.fbn' % (x*1e-6)

width = .8

with open('population.csv') as f:
    years = map(int, f.readline().split(',')[1:])
    dtype = [('continents', 'S16')] + [('', np.int32)]*len(years)
    y = np.loadtxt(f, delimiter=',', dtype=dtype)
    y = y.view(np.dtype([('continents','S16'), ('data', np.int32, len(years))]))
    data = y['data']
    continents = y['continents']
    bottom = np.zeros(len(years))
    for i in range(len(data)):
        bt = plt.bar(range(len(data[i])), data[i], width=width,
                     color=cm.hsv(32*i), label=continents[i],
                     bottom=bottom)
        bottom += data[i]
    plt.xticks(np.arange(len(years)) + width/2,
               [int(year) for year in years])
    plt.xlabel('Years')
    plt.ylabel('Population (in billions)')
    plt.title('World population')

    plt.legend(loc='upper left',
               prop=font_manager.FontProperties(size=7))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))
    plt.savefig('foo.png')
