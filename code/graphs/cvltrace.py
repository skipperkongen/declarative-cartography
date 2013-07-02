__author__ = 'kostas'
from datetime import datetime
import re


class TraceReader(object):

    def __init__(self, trace_path):
        with open(trace_path, 'r') as f:
            traces = []
            current_trace = None
            for line in f:
                line = line.strip()
                event = self._parse_line(line)
                if event['event'] == 'BEGIN_TRANSACTION':
                    current_trace = Trace(ts_begin=event['timestamp'], trace_name=event['jobname'])
                elif event['event'] == 'COMMIT':
                    current_trace.end(event['timestamp'])
                    traces.append(current_trace)
                    current_trace = None
                else:
                    current_trace.add_event(event)
        self._traces = traces

    def get_traces(self):
        return self._traces

    def _parse_line(self, line):
        # example:
        # 01/07/2013 11:11:54.207973 [7k_pt_airports_cellbound16_bound] found_conflicts 12
        # fields[0]  fields[1]       fields[2]                          fields[3]       fields[4:]

        # strftime("%d/%m/%Y %H:%M:%S.%f")
        fields = line.split(" ")
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
        self._last_ts = ts_begin
        self.ts_end = None
        # extract solver and constraint from jobname
        self.name = trace_name
        match = re.search('(bound|lp|heuristic)', trace_name)
        self.solver = match.group(1) if match else None
        match = re.search('(proximity[0-9]+|cellbound[0-9]+)', trace_name)
        self.constraint = match.groups() if match else None
        # private stuff
        self._init_info = {'operations': {}}
        self._levels = {}
        self._stats = {}

    def add_event(self, event):

        time_passed = event['timestamp'] - self._last_ts

        if event['event'] == 'INITIALIZED':
            self._init_info['operations']['initialize'] = time_passed

        elif event['event'] == 'MERGED_PARTITIONS':
            self._init_info['operations']['merge_partitions'] = time_passed

        elif event['event'] == 'INITIALIZED_LEVEL':
            # begin new level
            self._current_level = {
                'begin': self._last_ts,
                'num_records': 0,
                'agg_rank': 0,
                'operations': {}
            }
            self._current_level['operations']['initialize_level'] = time_passed
            zoom = event['value']
            self._levels[zoom] = self._current_level

        elif event['event'] == 'FINALIZED_LEVEL':
            self._current_level['duration'] = event['timestamp'] - self._current_level['begin']
            del self._current_level['begin']
            self._current_level['operations']['finalize_level'] = time_passed

        elif event['event'] == 'FORCED_LEVEL':
            self._current_level['operations']['force_level'] = time_passed

        elif event['event'] == 'FOUND_CONFLICTS':
            self._current_level['operations']['find_conflicts'] = time_passed

        elif event['event'] == 'RESOLVED_CONFLICTS':
            self._current_level['operations']['resolve_conflicts'] = time_passed

        elif event['event'] == 'TRANSFORMED_LEVEL':
            self._current_level['operations']['transform_level'] = time_passed

        elif event['event'] == 'STATS':
            self._stats[event['value']['cvl_zoom']] = event['value']

        elif event['event'] == 'STATS2':
            self.num_records = event['value']['total_recs']
            self.total_rank = event['value']['total_rank']

        else:
            raise Exception('unhandled event: {0:s}'.format(event['event']))

        self._last_ts = event['timestamp']

    def end(self, ts_end):
        self.ts_end = ts_end
        self.duration = self.ts_end - self.ts_begin
        # update levels
        records_remain = self.num_records
        rank_remain = self.total_rank
        for foo in bar:
            records_remain -= self._stats[i]
            pass

