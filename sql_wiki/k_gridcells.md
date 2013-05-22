# Using Grid

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

## Experiments with running time

Using OpenStreetMap streets in the Copenhagen region (57,812 records). There is a GIST index on wkb_geometry.


