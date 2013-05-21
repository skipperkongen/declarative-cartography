# Geometry to grid-snapped point set

**Description**: A function that takes a geometry (point, linestring, polygon) and returns a set of (grid-snapped) points that represent the extent of the input geometry

Function ST_Cellify:

```sql
DROP FUNCTION IF EXISTS ST_Cellify(geometry, float8, float8, float8, float8);
CREATE OR REPLACE FUNCTION ST_Cellify(
    geom geometry,
    cell_size float8,
    x0 float8 DEFAULT 0, y0 float8 DEFAULT 0,
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
WHERE ST_DWithin(PT.pt, $1, sqrt(2*$2*$2)/2)
;
$$ LANGUAGE sql IMMUTABLE STRICT;
```

Try out the function on a street from OSM:

```sql
SELECT 
  ST_Cellify(R.wkb_geometry, 100, 0, 0)) as pt,
  R.name,
  ST_Length(R.wkb_geometry) AS length
FROM 
  (
	SELECT * FROM denmark_highway WHERE name <> '' LIMIT 1
  ) R;
```