
-- SQL generated by CVL compiler

BEGIN;

---------------------
-- CVL Main: setup --
---------------------

-- Create output table

CREATE TABLE cph_highway_output AS
SELECT 
  *, 
  ST_Length(wkb_geometry) AS _rank, 
  type AS _partition, 
  15 as _tile_level 
FROM
  cph_highway;

-- Spatial index on output table

CREATE INDEX cph_highway_output_gist ON cph_highway_output USING GIST(wkb_geometry);

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

-----------------------------
-- CVL Main: create levels --
-----------------------------

---------------------------
-- Create zoom-level 14
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 14 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 14 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 14 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 14
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 14
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 14
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 14
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 14 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 14
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 13
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 13 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 13 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 13 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 13
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 13
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 13
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 13
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 13 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 13
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 12
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 12 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 12 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 12 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 12
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 12
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 12
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 12
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 12 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 12
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 11
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 11 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 11 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 11 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 11
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 11
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 11
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 11
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 11 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 11
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 10
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 10 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 10 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 10 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 10
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 10
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 10
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 10
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 10 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 10
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 9
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 9 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 9 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 9 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 9
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 9
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 9
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 9
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 9 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 9
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 8
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 8 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 8 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 8 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 8
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 8
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 8
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 8
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 8 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 8
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 7
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 7 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 7 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 7 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 7
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 7
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 7
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 7
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 7 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 7
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 6
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 6 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 6 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 6 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 6
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 6
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 6
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 6
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 6 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 6
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 5
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 5 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 5 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 5 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 5
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 5
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 5
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 5
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 5 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 5
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 4
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 4 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 4 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 4 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 4
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 4
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 4
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 4
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 4 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 4
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 3
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 3 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 3 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 3 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 3
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 3
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 3
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 3
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 3 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 3
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 2
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 2 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 2 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 2 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 2
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 2
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 2
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 2
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 2 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 2
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 1
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 1 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 1 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 1 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 1
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 1
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 1
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 1
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 1 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 1
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;

---------------------------
-- Create zoom-level 0
---------------------------

-- copy-down level

INSERT INTO cph_highway_output
SELECT ogc_fid, wkb_geometry, type, name, oneway, lanes, _rank, _partition, 0 as _tile_level
FROM cph_highway_output
WHERE _tile_level = 0 + 1;

-- CellboundConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

CREATE TEMPORARY TABLE _cellbound_1 AS 
(
	SELECT
		ST_PointHash(ST_Cellify(wkb_geometry, ST_CellSizeZ( 0 ), 0, 0 )) || _partition AS cell_id,
		ogc_fid AS record_id,
		_rank
	FROM 
		cph_highway_output
	WHERE 
		_tile_level = 0
);

INSERT INTO _conflicts 
SELECT 
	c.cell_id as conflict_id, 
	c.record_id, 
	c._rank, 
	f.min_hits
FROM 
	_cellbound_1 c
JOIN
(
	-- Find all cells with more than K records
	SELECT 
		cell_id, 
		count(*) - 16 AS min_hits
	FROM 
		_cellbound_1
	GROUP BY 
		cell_id
	HAVING 
		count(*) > 16
) f 
ON c.cell_id = f.cell_id;

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 0
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _cellbound_1;

DROP TABLE _conflicts;

-- AllOrNothingConstraint

CREATE TEMPORARY TABLE _conflicts(conflict_id text, record_id integer, _rank float, min_hits integer);

INSERT INTO _conflicts 
SELECT 
  ogc_fid AS conflict_id, 
  ogc_fid AS record_id, 
  1 AS record_rank, 
  1 AS min_hits 
FROM 
  cph_highway_output
WHERE
  _tile_level = 0
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output
    WHERE 
      _tile_level= 0
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      cph_highway_output 
    WHERE
      _tile_level = 0 + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);

DELETE FROM cph_highway_output
WHERE 
    _tile_level = 0
AND ogc_fid IN
(

  -- N Hitting Set heuristic
  SELECT h.record_id AS ogc_fid 
  FROM (
    SELECT ROW_NUMBER() OVER (PARTITION BY conflict_id ORDER BY _rank) AS r, record_id, min_hits
    FROM _conflicts
  ) h
  WHERE h.r <= h.min_hits

);

DROP TABLE _conflicts;
UPDATE cph_highway_output SET wkb_geometry = ST_Simplify(wkb_geometry, ST_ResZ(_tile_level, 256)/2);
------------------------
-- CVL Main: clean up --
------------------------

ALTER TABLE cph_highway_output DROP COLUMN _rank, DROP COLUMN _partition;

COMMIT;

