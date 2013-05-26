class CvlMain(object):
	"""docstring for CvlMain"""
	def __init__(self, hittingset_impl, constraints_impl, **query):
		super(CvlMain, self).__init__()
		self.hittingset = hittingset_impl
		self.constraints = constraints_impl
		self.query = query
	
	def generate_sql(self):
		code = []
		code.append("BEGIN;")
		code.extend(self.setup())
		code.extend(self.create_levels())
		code.extend(self.cleanup())
		code.append("COMMIT;")
		return code
		
	def setup(self):
		"""TODO"""
		code = []
		sql = """---------------------
-- CVL Main: setup --
---------------------
		
-- Create output table

CREATE TABLE {table} AS
SELECT 
	*, 
	{rank_by} AS _rank, 
	{partition_by} AS _partition,
	{zoomlevels} as _tile_level 
FROM {datasource};

-- Spatial index on output table

CREATE INDEX {table}_gist ON {table} USING GIST({geometry});

-- Add stored procedures

-- ST_PointHash

CREATE OR REPLACE FUNCTION ST_PointHash(
	pt geometry,
	OUT geohash text)
RETURNS text AS
$$
SELECT ST_GeoHash(
	ST_Transform(
		$1, 
		4326)) AS geohash;
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_Cellify

CREATE OR REPLACE FUNCTION ST_Cellify(
    geom geometry,
    cell_size float8,
    x0 float8 DEFAULT 0, 
	y0 float8 DEFAULT 0,
    OUT pt geometry)
RETURNS SETOF geometry AS
$$
SELECT * FROM (SELECT 
  ST_SnapToGrid(
    ST_SetSrid(
      ST_Point( 
        ST_XMin($1) + i*$2, 
        ST_YMin($1) + j*$2
      ),
      ST_Srid($1)
    ),
  $2, 
  $3, 
  $2, 
  $2
) AS pt
FROM
    generate_series(0, (ceil(ST_XMax( $1 ) - ST_Xmin( $1 )) / $2)::integer) AS i,
    generate_series(0, (ceil(ST_YMax( $1 ) - ST_Ymin( $1 )) / $2)::integer) AS j) PT
WHERE 
	$1 && ST_Envelope(ST_Buffer(PT.pt, $2/2)) 
	AND ST_Intersects($1, ST_Envelope(ST_Buffer(PT.pt, $2/2)));
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_ResZ

DROP FUNCTION IF EXISTS ST_ResZ(integer,integer);
CREATE OR REPLACE FUNCTION ST_ResZ(
	z integer,
	tilesize integer,
	OUT meter_per_pixel float)
RETURNS float AS
$$
SELECT (40075016.68 / power(2, $1)) / $2
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_CellSizeZ

CREATE OR REPLACE FUNCTION ST_CellSizeZ(
	z integer,
	OUT meter_per_pixel float)
RETURNS float AS
$$
SELECT 40075016.68 / power(2, $1)
$$ LANGUAGE sql IMMUTABLE STRICT;
""".format(**self.query)
		code.append(sql)
		return code

	def create_levels(self):
		"""TODO"""
		code = []
		sql = """-----------------------------
-- CVL Main: create levels --
-----------------------------
"""
		code.append(sql)
		return code

	def cleanup(self):
		"""TODO"""
		code = []
		sql = """------------------------
-- CVL Main: clean up --
------------------------

ALTER TABLE {table} DROP COLUMN _rank, DROP COLUMN _partition;
""".format(**self.query)
		code.append( sql )
		return code

if __name__ == '__main__':
	query = {
		'datasource': 'cph_highway',
		'table': 'cph_highway_output',
		'id': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'zoomlevels': 15,
		'rank_by': 'ST_Length(wkb_geometry)',
	 	'partition_by' : 'type'
	}
	cm = CvlMain(None, None, **query)
	print "\n".join(cm.generate_sql())
		
		


		
		