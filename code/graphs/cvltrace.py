__author__ = 'kostas'
from datetime import datetime


class TraceReader(object):

    def __init__(self, trace_path):
        with open(trace_path, 'r') as f:
            traces = []
            current_trace = None
            for line in f:
                line = line.strip()
                event = self.parse_line(line)
                if event['event'] == 'BEGIN_TRANSACTION':
                    current_trace = Trace(ts_begin=event['timestamp'], trace_name=event['jobname'])
                elif event['event'] == 'END_TRANSACTION':
                    current_trace.end(event['timestamp'])
                    traces.append(current_trace)
                else:
                    current_trace.add_event(event)

    def parse_line(self, line):
        # example:
        # 01/07/2013 11:11:54.207973 [7k_pt_airports_cellbound16_bound] found_conflicts 12
        # fields[0]  fields[1]       fields[2]                          fields[3]       fields[4:]

        # strftime("%d/%m/%Y %H:%M:%S.%f")
        fields =  line.split(" ")
        date_str = "{0:s} {1:s}".format(fields[0], fields[1])
        value = None if len(fields) <= 4 else eval(" ".join(fields[4:]))
        return {
            'timestamp': datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S.%f'),
            'jobname': fields[2],
            'event': fields[3].upper(),
            'value': value
        }


class Trace(object):

    def __init__(self, ts_begin=None, trace_name=None):
        self.ts_begin = ts_begin
        self.last_event_ts = ts_begin
        self.ts_end = None
        self.name = trace_name
        self.total_rank = -1
        self.total_recs = -1
        self.initialize = []
        self.levels = []

    def add_event(self, event):
        self.events.append(event)

    def end(self, ts_end):
        self.ts_end = ts_end

    def duration(self):
        return self.ts_end - self.ts_begin

ex = {
    'initialize': {
        'operations': []
    },
    'levels': [
        {'total_time': 42, 'rank_remaining': 42, 'records_remaining': 42, 'operations': []}
    ]
}

