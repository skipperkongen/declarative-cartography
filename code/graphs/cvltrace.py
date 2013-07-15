__author__ = 'kostas'
from datetime import datetime

class TraceReader(object):

    def __init__(self, trace_path):
        with open(trace_path, 'r') as f:
            self.traces = []
            self.current_trace = None
            for line in f:
                line = line.strip()
                event_dict = self.get_event_dictionary(line)
                self.handle_event(event_dict)

    def get_traces(self):
        return self.traces

    def get_event_dictionary(self, line):
        fields = line.split(" ")
        date_str = "{0:s} {1:s}".format(fields[0], fields[1])
        value = None if len(fields) <= 4 else eval(" ".join(fields[4:]))
        return {
            'timestamp': datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S.%f'),
            'jobname': fields[2],
            'event': fields[3].upper(),
            'value': value
        }

    def handle_event(self, event):
        """
        Three cases:
            BEGIN TRANSACTION: create new trace object
            COMMIT: append current trace object to traces list
            OTHER: add information to current trace (handled by trace object)
        """
        if event['event'] == 'BEGIN_TRANSACTION':
            self.current_trace = Trace(ts_begin=event['timestamp'], trace_name=event['jobname'])
        elif event['event'] == 'COMMIT':
            self.current_trace.end(event['timestamp'])
            self.traces.append(self.current_trace)
            self.current_trace = None
        else:
            # HANDLE OTHER EVENT
            self.current_trace.add_event(event)


class Trace(object):

    def __init__(self, ts_begin=None, trace_name=None):
        self.ts_begin = ts_begin
        self._last_ts = ts_begin
        self.ts_end = None
        # extract solver and constraint from jobname
        self.name = trace_name
        # private stuff
        self.initialization = None
        self.solver = None
        self.constraints = None
        self.inputstats = None
        self.levels = []
        self.current_level = None

    def add_event(self, event):

        time_passed = event['timestamp'] - self._last_ts
        event_type = event['event']

        if event_type == 'INITIALIZED':
            self.initialization = time_passed

        elif event_type == 'SOLVER':
            self.solver = event['value']

        elif event_type == 'CONSTRAINTS':
            self.constraints = event['value']

        elif event_type == 'INPUTSTATS':
            self.inputstats = event['value']

        elif event_type == 'INITIALIZED_LEVEL':
            self.current_level = {
                'zoom': event['value'],
                'timing': {'initialized_level': time_passed}
            }

        elif event_type == 'FOUND_CONFLICTS':
            self.current_level['timing']['found_conflicts'] = time_passed

        elif event_type == 'RESOLVED_CONFLICTS':
            self.current_level['timing']['resolved_conflicts'] = time_passed

        elif event_type == 'LEVELSTATS':
            self.current_level['levelstats'] = event['value']
            self.current_level['timing']['levelstats'] = time_passed

        elif event_type == 'FINALIZED_LEVEL':
            self.levels.append(self.current_level)
            self.current_level['timing']['finalized_level'] = time_passed

        else:
            raise Exception('unhandled event: {0:s}'.format(event_type))

        self._last_ts = event['timestamp']

    def end(self, ts_end):
        self.ts_end = ts_end
        self.duration = self.ts_end - self.ts_begin

