# How many OSM motorways per cell around Copenhagen?

```sql
CREATE OR REPLACE FUNCTION ST_CellSizeZ
(
  z integer,
  OUT meter_per_pixel float
) RETURNS float AS
$$
SELECT 40075016.68 / power(2, $1)
$$ LANGUAGE sql IMMUTABLE STRICT;

SELECT 
	Count(*)
FROM 
	cph_highway 
WHERE 
	ST_Intersects(
		wkb_geometry, 
		ST_Envelope(st_buffer(ST_SetSRID(ST_MakePoint(1389728,7494466),3857), ST_CellSizeZ(10)/2 ))
	)
AND 
	type IN ('motorway','motorway_link','motorway_junction','trunk', 'trunk_link');
```

Answer was a whooping 505... a bit more than I expected to be honest.