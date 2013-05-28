from constraints import cellbound, proximity, allornothing 
from algo.hittingset import HittingSetHeuristic

INFO_COMMENT = \
"""
-----------------------------------
-- SQL generated by CVL compiler --
-----------------------------------
-- Zoom-levels {zoomlevels}
-- Partition by: {partition_by}
-- Rank by: {rank_by}
-----------------------------------
"""

BEGIN_TX = \
"""
BEGIN;
"""

COMMIT_TX = \
"""
COMMIT;
"""

COPY_DOWN = \
"""
-- copy-down level

INSERT INTO {table}
SELECT {id}, {geometry}, {other}, _rank, _partition, {current_z} as _tile_level
FROM {table}
WHERE _tile_level = {current_z} + 1;
"""

DELETE_FROM = \
"""
DELETE FROM {table}
WHERE 
    _tile_level = {current_z}
AND {id} IN
(
{n_hitting_set}
);
"""

SET_UP = \
"""
---------------------
-- CVL Main: setup --
---------------------

-- Create output table
-- remove this when done testing
DROP TABLE IF EXISTS {table};

CREATE TABLE {table} AS
SELECT 
  *, 
  {rank_by} AS _rank, 
  {partition_by} AS _partition, 
  {zoomlevels} as _tile_level 
FROM
  {datasource};

-- Spatial index on output table

CREATE INDEX {table}_gist ON {table} USING GIST({geometry});

-- Add stored procedures

-- ST_PointHash

CREATE OR REPLACE FUNCTION ST_PointHash
(
  pt geometry,
  OUT geohash text
) RETURNS text AS
$$
SELECT 
  ST_GeoHash
  (
    ST_Transform
    (
      $1, 
      4326
    )
  ) AS geohash;
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_Cellify

CREATE OR REPLACE FUNCTION ST_Cellify
(
  geom geometry,
  cell_size float8,
  x0 float8 DEFAULT 0, 
  y0 float8 DEFAULT 0,
  OUT pt geometry
) RETURNS SETOF geometry AS
$$
SELECT * 
FROM  
(
  SELECT 
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
AND 
  ST_Intersects($1, ST_Envelope(ST_Buffer(PT.pt, $2/2)));
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_ResZ

CREATE OR REPLACE FUNCTION ST_ResZ
(
  z integer,
  tilesize integer,
  OUT meter_per_pixel float
) RETURNS float AS
$$
SELECT (40075016.68 / power(2, $1)) / $2
$$ LANGUAGE sql IMMUTABLE STRICT;

-- ST_CellSizeZ

CREATE OR REPLACE FUNCTION ST_CellSizeZ
(
  z integer,
  OUT meter_per_pixel float
) RETURNS float AS
$$
SELECT 40075016.68 / power(2, $1)
$$ LANGUAGE sql IMMUTABLE STRICT;
"""

CLEAN_UP = \
"""
------------------------
-- CVL Main: clean up --
------------------------

ALTER TABLE {table} DROP COLUMN _rank;
-- ALTER TABLE {table} DROP COLUMN _rank, DROP COLUMN _partition;
"""

CLEAN_UP_LEVEL = \
"""
DROP TABLE _conflicts;
"""

CREATE_LEVELS_HEADER = \
"""
-----------------------------
-- CVL Main: create levels --
-----------------------------
"""

CREATE_LEVEL_Z_HEADER = \
"""
---------------------------
-- Create zoom-level {current_z}
---------------------------
"""

CREATE_TEMP_TABLE_CONFLICTS = \
"""
CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);
"""

INSPECTION_HELPER = \
"""
-- SELECT count(*) FROM {table} GROUP BY _tile_level ORDER BY _tile_level

-- SELECT DISTINCT _partition FROM {table} where _tile_level={zoomlevels}
-- EXCEPT
-- SELECT DISTINCT _partition FROM {table} where _tile_level=0
"""

INSERT_INTO_CONFLICTS = \
"""
INSERT INTO _conflicts 
SELECT fc.* FROM ({constraint_select}) fc
WHERE fc._partition NOT IN ({forced_partitions});
"""

class CvlMain(object):
	"""docstring for CvlMain"""
	def __init__( self, hittingset_impl, constraints_impl, **query ):
		super( CvlMain, self ).__init__()
		self.hittingset = hittingset_impl
		self.constraints = constraints_impl
		self.query = query
	
	def generate_sql(self):
		code = []
		code.append( INFO_COMMENT.format( **self.query ))
		code.append( BEGIN_TX )
		code.extend( self.setup() )
		code.extend( self.create_levels() )
		code.extend( self.finalize() )
		code.extend( self.cleanup() )
		code.append( COMMIT_TX )
		code.append( INSPECTION_HELPER.format( **self.query ))
		return "".join( code )
		
	def setup(self):
		"""TODO"""
		code = []
		sql = SET_UP.format( **self.query )
		code.append( sql )
		return code

	def create_levels(self):
		"""TODO"""
		code = []
		code.append( CREATE_LEVELS_HEADER )
		for current_z in reversed(range( self.query['zoomlevels'] )):
			code.extend( self.create_level_z( current_z ))
		
		return code
	
	def create_level_z(self, current_z ):
		code = []
		format_obj = dict( self.query.items() + [('current_z', current_z), ('n_hitting_set', "".join(self.hittingset.solver_sql()))] )
		code.append( CREATE_LEVEL_Z_HEADER.format( **format_obj ))
		code.append(COPY_DOWN.format( **format_obj ))
		
		for constraint in self.constraints:
			code.append("\n-- " + constraint.__class__.__name__ + "\n")
			code.append( CREATE_TEMP_TABLE_CONFLICTS )
			# set up
			code.extend(constraint.set_up(current_z))
			# insert conflicts into _conflicts
			format_obj['constraint_select'] = "".join(constraint.find_conflicts(current_z))
			code.append(INSERT_INTO_CONFLICTS.format(**format_obj))
			# delete records to resolve conflicts
			code.append(DELETE_FROM.format( **format_obj ))
			# clean up
			code.extend(constraint.clean_up( current_z ))
			code.append( CLEAN_UP_LEVEL )
		return code
		
	def cleanup(self):
		"""TODO"""
		code = []
		sql = CLEAN_UP.format(**self.query)
		code.append( sql )
		return code
	
	def finalize(self):
		if self.query['simplify']:
			return ["UPDATE {table} SET {geometry} = ST_Simplify({geometry}, ST_ResZ(_tile_level, 256)/2);".format(
			**self.query
			)]
		else:
			return []

if __name__ == '__main__':
	query = {
		'datasource': 'cph_highway',
		'table': 'cph_highway_output',
		'id': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': 'type, name, oneway, lanes',
		'zoomlevels': 15,
		'rank_by': 'ST_Length(wkb_geometry)',
	 	'partition_by' : 'type',
		'_k': 16.0,
		'simplify': True
	}
	cm = CvlMain(HittingSetHeuristic(**query), [cellbound.CellboundConstraint(**query), allornothing.AllOrNothingConstraint(**query)], **query)
	print cm.generate_sql() # Query returned successfully with no result in 68070 ms on MacBook Pro
	
		
		


		
		