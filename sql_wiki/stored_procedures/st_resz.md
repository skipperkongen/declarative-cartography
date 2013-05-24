# ST_ResZ

PL/pgSQL version of [meter_per_pixel_3857](../../python_wiki/meter_per_pixel.md).

Compute the resolution (meter/pixel) at zoom-level *z* in EPSG:3857.

```sql
DROP FUNCTION IF EXISTS ST_ResZ(integer,integer);
CREATE OR REPLACE FUNCTION ST_ResZ(
	z integer,
	tilesize integer,
	OUT meter_per_pixel float)
RETURNS float AS
$$
SELECT (40075016.68 / power(2, $1)) / $2
$$ LANGUAGE sql IMMUTABLE STRICT;
```

Example usage:

```sql
SELECT ST_ResZ(15,256)
```