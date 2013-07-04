WILDCARD = '*'
from cvl.util.anonobject import Object
import pdb

class Query(object):
    """docstring for Query"""

    def __init__(self,
                 zoomlevels, input, fid, geometry,
                 output='cvl_output', other=None, rank_by='1',
                 subject_to=None):
        super(Query, self).__init__()
        # optional stuff defaults
        other = [] if other is None else other
        subject_to = [] if subject_to is None else subject_to
        # set all options
        self.zoomlevels = zoomlevels
        self.input = input
        self.output = output
        self.fid = fid
        self.geometry = geometry
        self.other = ', '.join(other) + ', '
        self.rank_by = rank_by
        self.subject_to = [Object(name=x[0],params=x[1:]) for x in subject_to]
