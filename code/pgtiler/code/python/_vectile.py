import psycopg2
import traceback
import sys

from shapely.wkt import dumps as wkt_dumps
from shapely.wkt import loads as wkt_loads
from shapely.geometry import asShape
from geojson import dumps as geojson_dumps 
import geojson

table = ""
id_column = "gid"
geometry_column = "geom"
attribute_columns = ["natural", "name"]
orig_prefix = "orig_"

# TODO Use geojson feature class instead
class Feature(object):

	def __init__(self, fid, geometry, properties, **extra):
		self.fid = fid
		self.geometry = geometry
		self.properties = properties

	def toGeoJSON(self):
		return geojson.Feature(id=self.fid, geometry=self.geometry, properties=self.properties )
		
	def __str__(self):
		geojson_dumps(self.toGeoJSON())
				
	def __repr__(self):
		return self.__str__()

# TODO Use geojson featurecollection class instead
class FeatureCollection(object):

	def __init__(self, features):
		self.features = features
	
	def toGeoJSON(self):
		return geojson.FeatureCollection([f.toGeoJSON() for f in self.features])
	
	def toBSON(self):
		return bson.dumps(self.__str__())
	
	def __str__(self):
		return geojson_dumps(self.toGeoJSON())

	def __repr__(self):
		return self.__str__()

def get_vector_tile_geojson(minx, miny, maxx, maxy):
	try:
		conn = psycopg2.connect("dbname='greenland_osm_shp' user='postgres' host='localhost' password='postgres'")
		cur = conn.cursor()
		bbox_wkt = create_bbox_as_wkt_linestring(minx, miny, maxx, maxy)
		select_stm = make_statement(bbox_wkt)
		cur.execute(select_stm)
		rows = cur.fetchall()
		features = []
		
		for row in rows:
			original_type = row[0]
			fid = row[1]
			geom = wkt_loads(row[2])
			attributes = dict([(attribute_columns[i], row[i+3]) for i in range(len(attribute_columns))])
			attributes["%sgeomtype" % orig_prefix] = original_type

			features.append( Feature(fid, geom, attributes) )
		conn.close()
		featurecollection = FeatureCollection( features )
		return featurecollection
	except:
		traceback.print_exc()
		print "I am unable to connect to the database"
		sys.exit(0)
	
def make_statement(bbox_wkt):
	# TODO add simplify....tricky because of units...argh
	
	escaped_attributes_columns = map(lambda x: '"%s"' % x, attribute_columns)
	attribute_part = ",%s" % (",".join( escaped_attributes_columns )) if attribute_columns else ""
	orig_geomtype_columnname = "%sgeomtype" % orig_prefix
	
	return """
		select
			GeometryType({3}) as "{0}",
			{2},
			st_astext(
				st_intersection(
					st_setsrid('{1}'::geometry, 4326), 
					st_setsrid({3}, 4326)
				)
			) as {3}{4}
		from 
			greenland_coastline 
		where 
			st_intersects(
				st_setsrid('{1}'::geometry, 4326), 
				st_setsrid({3}, 4326)
			);
	""".format(orig_geomtype_columnname, bbox_wkt, id_column, geometry_column, attribute_part)

def create_bbox_as_wkt_linestring(minx, miny, maxx, maxy):
	
	# ST_GeomFromText('LINESTRING(75.15 29.53,77 29,77.6 29.5, 75.15 29.53)')	
	wkt = "POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))" % \
		(
			minx, miny,
			minx, maxy,
			maxx, maxy,
			maxx, miny,
			minx, miny
		)
	return wkt

if __name__=='__main__':
	if len(sys.argv) != 5:
		print "Usage: python vectile.py min_x min_y max_x max_y"
		sys.exit(1)
	minx = float(sys.argv[1])
	miny = float(sys.argv[2])
	maxx = float(sys.argv[3])
	maxy = float(sys.argv[4])
	
	vector_tile_geojson = get_vector_tile_geojson(minx, miny, maxx, maxy)
	#vector_tile_geojson = get_vector_tile_geojson(-51.748, 64.1704, -51.710, 64.1846)
	print vector_tile_geojson