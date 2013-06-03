WILDCARD = '*'

class Query(object):
	"""docstring for Query"""
	def __init__(self, 
			zoomlevels=None, input=None, output=None, fid=None, geometry=None, 
			other=[], rank_by='1', partition_by='1', merge_partitions=[],
			subject_to=[], force_level=[], transform_by=[]
		):
		super(Query, self).__init__()
		self.zoomlevels = zoomlevels
		self.input = input
		self.output = output
		self.fid = fid
		self.geometry = geometry
		self.other = ', '.join(other)
		self.rank_by = rank_by
		self.partition_by = partition_by
		self.merge_partitions = merge_partitions
		self.subject_to = subject_to
		self.force_level = map(lambda x: (x[0], min(x[1],zoomlevels)), force_level)
		self.transform_by = transform_by

		