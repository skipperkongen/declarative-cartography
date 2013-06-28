__author__ = 'kostas'


class TraceReader(object):

    def __init__(self, trace_path):
        with open(trace_path, 'r') as f:
            self.lines = [line.strip() for line in f]

class Trace(object):
    pass