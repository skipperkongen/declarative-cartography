# Computing K-density using grids

Problem: Given a uniform grid of cells, find all cells intersecting more than *K* features.

![Cells with number of features shown](https://docs.google.com/drawings/d/1blMf8QWoIA8jDU8VrjZ1Hslgx7Erly1AdYrcEc1GqsM/pub?w=339&amp;h=346)


## Approach

1. Use [ST_Cellify]() to compute grid cells for a geometry
2. Convert points to a unique hash (see below), selecting *hash, feature_id*
3. Finally, find all hash codes that occur more than K times. Create K sized conflict sets for these.

### Hashing functions

[ST_GeoHash](http://postgis.refractions.net/documentation/manual-svn/ST_GeoHash.html) computes the GeoHash of point, but only works for lat/long according to the GeoHash specification. What will happen when hashing coordinates in epsg:3857? A solution (if the GeoHashes collide when using 3857) is to use [ST_Transform](http://www.postgis.org/docs/ST_Transform.html) to convert to lat/long first and then geohash the point.

```sql
SELECT ST_GeoHash(ST_SetSRID(ST_MakePoint(-126,48),4326));
-- OR
SELECT ST_GeoHash(ST_Transform(ST_SetSRID(ST_MakePoint(-126,48),3857), 4326));
-- Total query runtime: 20 ms.
```

A simpler idea is to use [ST_AsText()](http://www.postgis.org/docs/ST_AsText.html) as the hash, but this takes up more space, which can be compressed to 64 bits using md5:


```sql
SELECT ST_AsText(ST_SetSRID(ST_MakePoint(-17654959.5761613, 8241354.5309193),3857));
-- Total query runtime: 21 ms.
-- OR
SELECT md5(ST_AsText(ST_SetSRID(ST_MakePoint(-17654959.5761613, 8241354.5309193),3857)));
-- Total query runtime: 22 ms.
```

Conlusion:

* I think the best approach is to use ST_GeoHash (with transform). It is faster, semantically meaningful and guaranteed to avoid collisions of cell hashes. I have created a function [ST_PointHash()](https://github.com/skipperkongen/phd_cvl/blob/master/sql_wiki/st_pointhash.md) that takes care of the transformation before the GeoHash is computed.

## Custom methods used

ST_PointHash():

```sql
DROP FUNCTION IF EXISTS ST_Hash(geometry);
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
```

ST_Cellify():

```sql
DROP FUNCTION IF EXISTS ST_Cellify(geometry, float8, float8, float8);
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
	AND ST_Intersects($1, ST_Envelope(ST_Buffer(PT.pt, $2/2)))
;
$$ LANGUAGE sql IMMUTABLE STRICT;
```

## Experiments with running time

Using OpenStreetMap streets in the Copenhagen region (57,812 records). There is a GIST index on wkb_geometry.

What is the time to compute the *cell,record_id* pairs?

```sql
SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, 100, 0, 0)) AS cell_id, 
	ogc_fid AS record_id
FROM cph_highway;
-- Total query runtime: 453740 ms. 7-8 minutes for 57,812 records
-- 382611 rows retrieved.
-- 1.2 ms per row
-- 7.8 ms per record
```

What is the time to compute cells that intersect more than K=16 records?

```sql
SELECT 
	c.cell_id, 
	count(c.*) as num_recs 
FROM
(SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, 100, 0, 0)) AS cell_id
FROM cph_highway) c
GROUP BY c.cell_id
HAVING count(*) > 16;
``` 


