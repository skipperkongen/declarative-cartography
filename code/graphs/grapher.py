__author__ = 'kostas'
from optparse import OptionParser

import sys

if __name__ == '__main__':
    usage = "usage: %prog [options] tracefile [tracefile] ..."
    parser = OptionParser(usage=usage)
    parser.add_option("-g", "--graph",
                      help="Type of graph to produce")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.print_usage()
        sys.exit(1)

