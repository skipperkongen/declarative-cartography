class CvlMain(object):
	"""docstring for CvlMain"""
	def __init__(self, hittingset_impl, constraints_impl, **query):
		super(CvlMain, self).__init__()
		self.hittingset = hittingset_impl
		self.constraints = constraints_impl
		self.query = query
	
	def generate_sql(self):
		code = []
		code.extend(self.setup())
		code.extend(self.create_levels())
		code.extend(self.cleanup())
		return code
		
	def setup(self):
		"""TODO"""
		code = []
		sql = """-- CVL Main: create output table
CREATE TABLE {table} AS
SELECT 
	*, 
	{rank} AS _rank, 
	{partition} AS _partition,
	{zoomlevels} as _tile_level 
FROM {datasource};
""".format(**self.query)
		code.append(sql)
		sql = """-- CVL Main: create index on output table
CREATE INDEX {table}_gist ON {table} USING GIST({geometry});
""".format(**self.query)
		code.append(sql)
		return code

	def create_levels(self):
		"""TODO"""
		code = []
		return code

	def cleanup(self):
		"""TODO"""
		code = []
		sql = """-- CVL Main: delete columns _rank and _partition
ALTER TABLE {table} DROP COLUMN _rank, DROP COLUMN _partition;
""".format(**self.query)
		code.append( sql )
		return code
		
		


		
		