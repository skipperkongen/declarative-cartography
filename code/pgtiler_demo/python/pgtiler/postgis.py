import psycopg2
import geojson

MAX_FEATURES = 0
TABLE_ALIAS = "foo"
RANDOM_STRING = "vctlqqq"

INDEXTILES = \
"""
SELECT 
	{fid},
	md5(foo.*::text) as rowhash
FROM 
	{table} foo
WHERE
	ST_Intersects({geometry}, {envelope});
"""

VECTORTILES = \
"""
SELECT 
	{fid},
	ST_AsGeoJSON(ST_Transform(ST_Simplify(ST_Intersection({geometry},{envelope}), {simplify_param}),{target_srid})) as the_geom,
	md5(foo.*::text) as rowhash,
	GeometryType({geometry}) as geomtype
	{other_columns}
FROM 
	{table} foo
WHERE
	ST_Intersects({geometry}, {envelope});
"""

ENVELOPE_TRANSF = \
"ST_Transform(ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, {srid}), {target_srid})"

ENVELOPE_NOTRANSF = "ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}, {srid})"

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
		self.data_srid = self._learn_srid()

	def _learn_srid():
		conn, cur = self.connect()
		cur.execute('SELECT ST_SRID({geometry}) FROM {table} LIMIT 1;'.format(geometry=self.geom_col, table=self.table))
		rows = cur.fetchall()
		self.data_srid = int(rows[0][0])
		conn.close()
	
	# Vectile interface
	
	def get_feature_ids(self, bbox, srid):
		return map(lambda row: self._row_to_feature(row, projections), rows)

	def get_features(self, bbox, srid, resolution=None, store_geom=None, map_rules=None):
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

	def connect(self):
		conn = psycopg2.connect("dbname='%s' host='%s' user='%s'  password='%s'" % (
			self.connection_settings.db_name,
			self.connection_settings.db_host,
			self.connection_settings.db_user,
			self.connection_settings.db_password
		))
		return conn, conn.cursor()
		
class PGConnectionSettings(object):
	"""docstring for PGSettings"""
	def __init__(self, db_name=None, db_host="localhost", db_user="postgres", db_password="postgres"):
		super(PGConnectionSettings, self).__init__()
		self.db_name = db_name
		self.db_host = db_host
		self.db_user = db_user
		self.db_password = db_password
				