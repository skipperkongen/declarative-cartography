WILDCARD = '*'
from cvl.util.anonobject import Object


class Query(object):
    """docstring for Query"""

    def __init__(self,
                 zoomlevels=None, input=None, output=None, fid=None, geometry=None,
                 other=[], rank_by='1', partition_by='1', merge_partitions=[],
                 subject_to=[], force_level=[], transform_by=[]
    ):
        super(Query, self).__init__()
        self.zoomlevels = zoomlevels
        self.zoomlevels = zoomlevels
        self.input = input
        self.output = output
        self.fid = fid
        self.geometry = geometry
        self.other = ', '.join(other)
        self.rank_by = rank_by
        self.partition_by = partition_by
        self.merge_partitions = [Object(before=x[0], after=x[1]) for x in merge_partitions]
        self.subject_to = [Object(name=x[0], params=list(x[1][1:])) for x in subject_to]
        self.force_level = [Object(partition=x[0], min_level=min(x[1], zoomlevels)) for x in force_level]
        self.transform_by = transform_by

		