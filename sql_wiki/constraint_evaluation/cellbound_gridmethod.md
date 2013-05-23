# Computing K-density using grids

Problem: Given a uniform grid of cells, find all cells intersecting more than *K* features.

![Cells with number of features shown](https://docs.google.com/drawings/d/1blMf8QWoIA8jDU8VrjZ1Hslgx7Erly1AdYrcEc1GqsM/pub?w=339&amp;h=346)

## Approach

1. Use [ST_Cellify]() to compute grid cells for a geometry
2. Convert points to a unique hash (see below), selecting *hash, feature_id*
3. Find hash codes with > K occurences. 
4. Select all K+1-sized sets of records for each cell hash.
5. Solve hitting set

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

### Computing the cells

What is the time to compute the *cell,record_id* pairs for cells of size *cell_size*?

```sql
SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, {cell_size}, 0, 0)) AS cell_id, 
	ogc_fid AS record_id
FROM cph_highway;
-- For cell_size = 100 meter
-- Total query runtime: 453740 ms. 7-8 minutes for 57,812 records
-- 382611 rows retrieved.
-- 1.2 ms per row
-- 7.8 ms per record
```

<table>
	<tr><th>cell size</th><th>rows retrieved</th><th>total running time</th><th>time per record (58K records total)</th></tr>
	<tr><td>100 meter</td><td>382611</td>        <td>7-8  minutes</td>      <td>7.8 ms/record</td></tr>
	<tr><td>200 meter</td><td>208562</td>        <td>2-3 minutes</td>       <td>2.3 ms/record</td></tr>
	<tr><td>400 meter</td><td>122803</td>        <td>1 minute</td>          <td>0.9 ms/record</td></tr>
    <tr><td>600 meter</td><td>95669</td>         <td>30 seconds</td>        <td>0.6 ms/record</td></tr>
    <tr><td>800 meter</td><td>82923</td>         <td>26 seconds</td>        <td>0.5 ms/record</td></tr>
    <tr><td>1000 meter</td><td>75666</td>         <td>22 seconds</td>       <td>0.4 ms/record</td></tr>
    <tr><td>1200 meter</td><td>71119</td>         <td>21 seconds</td>       <td>0.4 ms/record</td></tr>
</table>

Diagram of running time:

![Running time](https://raw.github.com/skipperkongen/phd_cvl/master/sql_wiki/images/runningtime_cellify.png?login=skipperkongen&token=aaa44d9bf680b94583f714709bb0ad3b)

### Computing cells with more than K records

What is the time to compute cells that intersect more than K=16 records, cell-size 100?

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
-- Total query runtime: 455842 ms.
-- 1 row retrieved.
``` 

The running time was the same as the query without *GROUP BY*. This tells me that the running time is dominated by computing *ST_Cellify()* and *ST_PointHash()*. How fast is it to compute just the cells without hashing (omitting the *GROUP BY*)?

```sql
SELECT 
	ST_Cellify(wkb_geometry, 100, 0, 0) AS cell_pt
FROM cph_highway;
-- Total query runtime: 451507 ms.
-- 382611 rows retrieved.
-- 
```

Conclusion: The running time is dominated by ST_Cellify for small cell sizes (100m).

What is the running time for larger cells (1km)?

```sql
SELECT 
	c.cell_id, 
	count(c.*) as num_recs 
FROM
(SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, 1000, 0, 0)) AS cell_id
FROM cph_highway) c
GROUP BY c.cell_id
HAVING count(*) > 16;
-- Total query runtime: 21528 ms.
-- 1515 rows retrieved.
```

For 10 times larger cell-size (1km) the query runs 21 times faster than with small cell-size (100m).

## Trick: Double cell-size, quadruple K

What is the benefit of counting average density for larger cells? Let's try doubling the cell-size and quadrupling the K. This is almost the same density measure (of course very local density is not captured by the bigger cells).

Time for cellsize=200m, K=4:

```sql
SELECT 
	c.cell_id, 
	count(c.*) as num_recs 
FROM
(SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, 200, 0, 0)) AS cell_id
FROM cph_highway) c
GROUP BY c.cell_id
HAVING count(*) > 4;
-- Total query runtime: 135977 ms.
-- 7441 rows retrieved.
```

Time for cellsize * 2 = 400m, K*4=16:

```sql
SELECT 
	c.cell_id, 
	count(c.*) as num_recs 
FROM
(SELECT 
	ST_PointHash(ST_Cellify(wkb_geometry, 400, 0, 0)) AS cell_id
FROM cph_highway) c
GROUP BY c.cell_id
HAVING count(*) > 16;
-- Total query runtime: 49926 ms.
-- 378 rows retrieved.
```

### Conclusion

While the running time is greatly reduced by using larger cell-sizes and quadrupling K, the query does not provide at all the same answer (7441 rows versus 378, which can not be explained by dividing 7441 by four).

## Connection to MapReduce

* Map: for each record emit all: (key=cell-id, value=record-id) 
* Reduce: Find cell-id, where count cell-id > K. Create K-sets of records that have given cell-id.

## Back-of-the-envelope: Scalability

How long would it take to compute 100m cells with more than K records for 40 million records? Assuming an equal distribution as OpenStreetMap streets. The cost is dominated by the ST_Cellify() function call.

At 7.8 ms per record, it would take 86 hours. Not so good...






