import psycopg2
import geojson

MAX_FEATURES = 0
TABLE_ALIAS = "foo"
RANDOM_STRING = "vctlqqq"

class PGSource(object):
	"""docstring for PostGISDataSource"""
	def __init__(self, connection_settings, table, fid_col="fid", geom_col="geom", property_cols=[], maprules=[]):
		super(PGSource, self).__init__()
		self.connection_settings = connection_settings
		self.table = table
		self.fid_col = fid_col
		self.geom_col = geom_col
		self.property_cols = property_cols
		self.maprules = maprules
		self.conn = None

	# RESUABLE PARTS

	def _envelope(self, bbox, srid):
		envelope = "ST_MakeEnvelope({0}, {1}, {2}, {3}, {4})".format(bbox.minx, bbox.miny, bbox.maxx, bbox.maxy, srid)
		return envelope
	
	def _transformed_geom(self, srid):
		transformed_geom = "ST_Transform({0}, {1})".format(self.geom_col, srid)
		return transformed_geom
	
	# SELECTIONS/PROJECTIONS

	def _id_digest_projection(self):
		# howto hash row: http://stackoverflow.com/questions/3878499/finding-the-hash-value-of-a-row-in-postgresql
		projections = [
			{
				"sql": "{0} as fid_{1}".format(self.fid_col, RANDOM_STRING), 
				"type": "id" },
			{
				"sql": "md5({0}.*::text) as rowhash_{1}".format(TABLE_ALIAS, RANDOM_STRING),
				"type": "property",
				"name": "digest" }
		]
		return projections
	
	def _feature_projection(self, bbox, srid, resolution, clip=True, result_srid=4326):
		
		transformed_geom = self._transformed_geom( srid )
		envelope = self._envelope( bbox, srid )

		# Clip geometries?
		if clip:
			transformed_geom = "ST_Intersection({0},{1})".format(transformed_geom, envelope)

		# Snap to grid?		
		if resolution:
			transformed_geom = "ST_Simplify({0}, {1})".format(transformed_geom, resolution)


		# Do final transform and convert to geojson
		geom_projection = "ST_AsGeoJSON(ST_Transform({0},{1})) as geom_{2}".format(transformed_geom, result_srid, RANDOM_STRING)
		
		projections = [
			{
				"sql": "{0} as fid_{1}".format(self.fid_col, RANDOM_STRING), 
				"type":"id" },			
			{
				"sql": geom_projection, 
				"type": "geometry" },
			{
				"sql": "md5({0}.*::text) as rowhash_{1}".format(TABLE_ALIAS, RANDOM_STRING), 
				"type": "property", 
				"name": "digest" },
			{
				"sql": "GeometryType({0}) as geomtype_{1}".format(self.geom_col, RANDOM_STRING),
				"type": "property",
				"name": "orig_geomtype"
			}
		]
		for prop_name in self.property_cols:
			projections.append(
			{
				"sql": "{0} as {0}_{1}".format(prop_name, RANDOM_STRING),
				"type": "property",
				"name": prop_name })
				
		return projections
	
	# WHERE CLAUSES

	def _id_in_where_clause(self, bbox, srid):
		pass

	def _bbox_where_clause(self, bbox, srid, resolution=None):
		print "Resolution: ", resolution
		transformed_geom = self._transformed_geom( srid )
		envelope = self._envelope( bbox, srid )
		clauses = [
			"{0} && {1}".format( transformed_geom, envelope ),
			"ST_Intersects({0},{1})".format(transformed_geom, envelope)
		]
		if resolution and self.maprules:
			clauses_from_rules = filter(lambda x: x is not None, map(lambda r: r(resolution), self.maprules))
			clauses.extend(clauses_from_rules)
		return clauses
	
	# SQL
	
	def _final_sql(self, projections, from_table, where_clauses, limit=0):
		projections_sql = map(lambda proj: proj["sql"], projections)
		sql = "SELECT {0} FROM {1} WHERE {2}".format(
			",".join( projections_sql ), 
			from_table, 
			" and ".join( where_clauses )
		)
		if limit > 0:
			sql = "{0} limit {1};".format(sql, MAX_FEATURES)
		else:
			sql = "{0};".format(sql)
		return sql

	def _execute(self, sql, projections):
		"""Return a list of objects implementing __geo_interface__ Features"""
		print "SQL: ",sql
		self.connect()
		cur = self.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		self.close()
		return map(lambda row: self._row_to_feature(row, projections), rows)
	
	def _row_to_feature(self, row, projections):
		#col_map {'id':0, 'geom':1, 'properties':[('digest', 2),('name':3),('type':4 )] }
		# convert to GeoJSON feature collection
		fid = None
		geometry = None
		properties = {}
		
		for i in range(len(projections)):
			proj = projections[i]
			if proj["type"] == "id":
				fid = row[i]
			elif proj["type"] == "geometry":
				geometry = geojson.loads(row[i])
			else:
				properties[ proj["name"] ] = row[i]
				
		return geojson.Feature(id = fid, geometry=geometry, properties=properties)
		
	# VECTILE INTERFACE
	
	def get_feature_ids(self, bbox, srid):
		"""Return a list of __geo_interface__ features without geometries, only an id and a digest property"""
		
		# select
		projections = self._id_digest_projection()
		
		# from
		from_table = "{0} {1}".format( self.table, TABLE_ALIAS )

		# where 
		where_clauses = self._bbox_where_clause( bbox, srid )
		
		# final sql
		sql = self._final_sql( projections, from_table, where_clauses )
				
		# execute
		return self._execute(sql, projections)
	
	def get_features_by_id(self, *ids):
		pass
		# TODO

	def get_features(self, bbox, srid, resolution=None, store_geom=None, map_rules=None):
		"""Implementation of vectile get_features interface"""
		
		# select
		projections = self._feature_projection( bbox, srid, resolution )
		
		# from
		from_table = "{0} {1}".format(self.table, TABLE_ALIAS)

		# where 
		where_clauses = self._bbox_where_clause( bbox, srid, resolution)
		
		# final sql
		sql = self._final_sql(projections, from_table, where_clauses, limit=MAX_FEATURES)
				
		# execute
		return self._execute(sql, projections)

	def connect(self):
		self.conn = psycopg2.connect("dbname='%s' host='%s' user='%s'  password='%s'" % (
			self.connection_settings.db_name,
			self.connection_settings.db_host,
			self.connection_settings.db_user,
			self.connection_settings.db_password
		))
		
	def close(self):
		self.conn.close()

class PGConnectionSettings(object):
	"""docstring for PGSettings"""
	def __init__(self, db_name=None, db_host="localhost", db_user="postgres", db_password="postgres"):
		super(PGConnectionSettings, self).__init__()
		self.db_name = db_name
		self.db_host = db_host
		self.db_user = db_user
		self.db_password = db_password
