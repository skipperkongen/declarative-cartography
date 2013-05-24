# ST_CellSizeZ

Compute the size of cells at zoom-level *z* in EPSG:3857

```sql
DROP FUNCTION IF EXISTS ST_CellSizeZ(integer);
CREATE OR REPLACE FUNCTION ST_CellSizeZ(
	z integer,
	OUT meter_per_pixel float)
RETURNS float AS
$$
SELECT 40075016.68 / power(2, $1)
$$ LANGUAGE sql IMMUTABLE STRICT;
```

Example usage:

```sql
SELECT ST_CellSizeZ(15)
-- Total query runtime: 21 ms.
```

By transforming coordinates to epsg:4326, the hash is guaranteed to be unique for a given cell center point.