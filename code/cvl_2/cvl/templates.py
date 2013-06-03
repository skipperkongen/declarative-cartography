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

HEADER_MERGE = \
"""
-- merging partitions
"""

MERGE_PARTITIONS = \
"""
UPDATE {output} SET _partition = '{after_merge}' WHERE _partition IN ({before_merge});
"""

MERGE_PARTITIONS_REST = \
"""
UPDATE {output} SET _partition = '{after_merge}' WHERE _partition NOT IN ({merged});
"""

SIMPLIFY = \
"""
-- simplifying records on all levels

UPDATE {output} SET {geometry} = ST_Simplify({geometry}, ST_ResZ(_tile_level, 256)/2);
"""

ALLORNOTHING = \
"""
SELECT 
  {fid} AS conflict_id, 
  {fid} AS record_id, 
  _rank, 
  _partition,
  1 AS min_hits 
FROM 
  {output}
WHERE
  _tile_level = {current_z}
AND
  _partition IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {output}
    WHERE 
      _tile_level= {current_z}
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {output} 
    WHERE
      _tile_level = {current_z} + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);
"""


RESOLVE_CONFLICTS = \
"""
-- resolve conflicts

DELETE FROM {output}
WHERE 
    _tile_level = {current_z}
AND {fid} IN
(
{conflict_resolution}
);
"""

SET_UP = \
"""
---------------------
-- CVL Main: setup --
---------------------

-- Create output table
-- remove this when done testing
DROP TABLE IF EXISTS {output};

CREATE TABLE {output} AS
SELECT 
  *, 
  {rank_by} AS _rank, 
  {partition_by} AS _partition, 
  {zoomlevels} as _tile_level 
FROM
  {input};

-- Spatial index on output table

CREATE INDEX {output}_gist ON {output} USING GIST({geometry});

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

HEADER_FINALIZE = \
"""
--------------------------
-- CVL Main: finalizing --
--------------------------
"""

FINALIZE = \
"""
-- ALTER TABLE {output} DROP COLUMN _rank, DROP COLUMN _partition;
"""

CREATE_LEVELS_HEADER = \
"""
-----------------------------
-- CVL Main: create levels --
-----------------------------
"""


INIT_LEVEL = \
"""
---------------------------
-- Create zoom-level {current_z}
---------------------------

-- copy-down level

INSERT INTO {output}
SELECT {fid}, {geometry}, {other}, _rank, _partition, {current_z} as _tile_level
FROM {output}
WHERE _tile_level = {current_z} + 1;

-- create empty _conflicts table

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);
"""

CLEAN_UP_LEVEL = \
"""
-- drop _conflicts

DROP TABLE _conflicts;
"""

HEADER_CONSTRAINT = \
"""
-- Constraint: {constraint_name}
"""


INSPECTION_HELPER = \
"""
-- SELECT _tile_level, _partition, count(*) FROM {output} GROUP BY _tile_level,_partition ORDER BY _tile_level, count(*)
"""

INSERT_INTO_CONFLICTS = \
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

FORCE_DELETE = \
"""
-- force deleting partition

DELETE FROM {output}
WHERE _tile_level = {current_z}
AND _partition = {delete_partition};
"""