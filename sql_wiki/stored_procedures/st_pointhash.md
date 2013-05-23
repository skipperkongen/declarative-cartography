# ST_PointHash

Stored procedure that converts a point (in any projection) to a GeoHash using the [ST_GeoHash](http://postgis.refractions.net/documentation/manual-svn/ST_GeoHash.html) function.

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

Example usage:

```sql
SELECT ST_GeoHash(ST_SetSRID(ST_MakePoint(-126,48),4326));
-- OR
SELECT ST_GeoHash(ST_Transform(ST_SetSRID(ST_MakePoint(-126,48),3857), 4326));
-- Total query runtime: 20 ms.
```

By transforming coordinates to epsg:4326, the hash is guaranteed to be unique for a given cell center point.