WILDCARD = '*'
from cvl.util.anonobject import Object
import pdb

class Query(object):
    """docstring for Query"""

    def __init__(self,
                 zoomlevels, input, fid, geometry,
                 output='cvl_output', other=None, rank_by='1', partition_by='1', merge_partitions=None,
                 subject_to=None, force_level=None, transform_by=None):
        super(Query, self).__init__()
        # optional stuff defaults
        other = [] if other is None else other
        merge_partitions = [] if merge_partitions is None else merge_partitions
        subject_to = [] if subject_to is None else subject_to
        force_level = [] if force_level is None else force_level
        transform_by = [] if transform_by is None else transform_by
        # set all options
        self.zoomlevels = zoomlevels
        self.input = input
        self.output = output
        self.fid = fid
        self.geometry = geometry
        self.other = ', '.join(other) + ', '
        self.rank_by = rank_by
        self.partition_by = partition_by
        self.merge_partitions = [Object(before=x[0], after=x[1]) for x in merge_partitions]
        self.subject_to = [Object(name=x[0],params=x[1:]) for x in subject_to]
        self.force_level = [Object(partition=x[0], min_level=min(x[1], zoomlevels)) for x in force_level]
        self.transform_by = transform_by
