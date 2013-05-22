# ST_PointHash

Stored procedure that converts a point (in any projection) to a GeoHash

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