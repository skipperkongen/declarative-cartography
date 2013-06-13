# BASIC TRANSACTION

BEGIN_TX = \
"""
BEGIN;
"""

COMMIT_TX = \
"""
COMMIT;
"""

# INIT

BIG_COMMENT_HEADER = \
"""
-----------------------------------
-- {comment}
-----------------------------------
"""

# FRAMEWORK

ADD_FRAMEWORK = \
"""
-- ST_CellSizeZ

CREATE OR REPLACE FUNCTION ST_CellSizeZ
(
  z integer,
  OUT meter_per_pixel float
) RETURNS float AS
$$
SELECT 40075016.68 / power(2, $1)
$$ LANGUAGE sql IMMUTABLE STRICT;

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
      $3 + $2/2, 
      $4 + $2/2, 
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

-- web mercator cells

CREATE OR REPLACE FUNCTION ST_WebMercatorCells
(
  geom geometry,
  zoom integer,
  OUT pt geometry
) RETURNS SETOF geometry AS
$$
SELECT
  ST_Cellify($1, ST_CellSizeZ($2), -20037508.34, -20037508.34) as pt
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
"""

REMOVE_FRAMEWORK = \
"""
DROP FUNCTION ST_PointHash(geometry);
DROP FUNCTION ST_WebMercatorCells(geometry, integer);
DROP FUNCTION ST_Cellify(geometry, float8, float8, float8);
DROP FUNCTION ST_ResZ(integer,integer);
DROP FUNCTION ST_CellSizeZ(integer);
"""

DROP_OUTPUT_TABLE = \
"""
DROP TABLE IF EXISTS {output};
"""

CREATE_OUTPUT_TABLE = \
"""
CREATE TABLE {output} AS
SELECT 
  *, 
  {rank_by} AS _rank, 
  {partition_by} AS _partition, 
  {zoomlevels} as _tile_level 
FROM
  {input};

CREATE INDEX {output}_gist ON {output} USING GIST({geometry});
"""

# CVL

MERGE_PARTITIONS = \
"""
UPDATE {output} SET _partition = '{after_merge}' WHERE _partition IN ({before_merge});
"""

MERGE_PARTITIONS_REST = \
"""
UPDATE {output} SET _partition = '{after_merge}' WHERE _partition NOT IN ({merged});
"""

# Stage commands

COPY_LEVEL = \
"""
INSERT INTO {output}
SELECT {fid}, {geometry}, {other}, _rank, _partition, {to_z} as _tile_level
FROM {output}
WHERE _tile_level = {from_z};
"""

INITIALIZE_LEVEL = \
"""
CREATE TEMPORARY TABLE _deletions (record_id integer);
CREATE TEMPORARY TABLE _conflicts (conflict_id text, record_id integer, _rank float, min_hits integer);
"""

FORCE_LEVEL = \
"""
DELETE FROM {output}
WHERE _tile_level = {current_z}
AND _partition = {delete_partition};
"""

FIND_CONFLICTS = \
"""
INSERT INTO _conflicts 
SELECT 
	s.conflict_id,
	s.record_id,
	s._rank,
	s.min_hits
FROM ({constraint_select}) s;
"""

FIND_CONFLICTS_IGNORE = \
"""
INSERT INTO _conflicts 
SELECT 
	s.conflict_id,
	s.record_id,
	s._rank,
	s.min_hits
FROM ({constraint_select}) s
WHERE s._partition NOT IN ({ignored_partitions});
"""

FIND_DELETIONS = \
"""
INSERT INTO _deletions 
SELECT sol.record_id FROM ({solution}) sol;
"""

DROP_EXPORT_TABLES = \
"""
DROP TABLE IF EXISTS {output}_export_conflicts;
DROP TABLE IF EXISTS {output}_export_deletions;
"""

CREATE_EXPORT_TABLES = \
"""
CREATE TABLE {output}_export_conflicts (conflict_id text, record_id integer, _rank float, min_hits integer, _tile_level integer);
CREATE TABLE {output}_export_deletions (record_id integer, _tile_level integer);
"""

EXPORT_LEVEL = \
"""
INSERT INTO {output}_export_conflicts
SELECT *, {current_z} as _tile_level FROM _conflicts;

INSERT INTO {output}_export_deletions
SELECT *, {current_z} from _deletions
"""

APPLY_DELETIONS = \
"""
DELETE FROM {output}
WHERE 
    _tile_level = {current_z}
AND {fid} IN (SELECT * FROM _deletions);
"""

ALLORNOTHING = \
"""
DELETE FROM {output}
WHERE _tile_level = {current_z}
AND _partition IN
(
  SELECT low._partition FROM 
  (
    SELECT _partition, count(*) AS count
    FROM {output}
    WHERE _tile_level= {current_z}
    GROUP BY _partition
  ) low 
  JOIN
  (
    SELECT _partition, count(*) AS count
    FROM {output} 
    WHERE _tile_level = {current_z} + 1
    GROUP BY _partition
  ) high
  ON low._partition = high._partition
  WHERE low.count < high.count);
"""

SIMPLIFY = \
"""
UPDATE {output} SET {geometry} = ST_Simplify({geometry}, ST_ResZ({current_z}, 256)/2) WHERE _tile_level={current_z};
"""

CLEAN_LEVEL = \
"""
DROP TABLE _conflicts;
DROP TABLE _deletions;
"""

# Finalizing

SIMPLIFY_ALL = \
"""
UPDATE {output} SET {geometry} = ST_Simplify({geometry}, ST_ResZ(_tile_level, 256)/2);
"""


# COMMENTS

COMMENT = \
"""
-- {comment}
"""

BIG_COMMENT_HEADER = \
"""
-----------------------------
-- {comment}
-----------------------------"""

BIG_COMMENT = \
"""
-- {comment}"""

BIG_COMMENT_FOOTER = \
"""
-----------------------------
"""


TRYTHIS = \
"""
-- SELECT _tile_level, _partition, Count(*) FROM {output} GROUP BY _tile_level, _partition ORDER BY _tile_level, _partition;
"""
