# Evaluating proximity constraint

Problem: Make sure no two records are too close to each other (in pixels)

## SQL

Continuing with the [example from README](../README.md) (modified to use only proximity constraint):

```cvl
GENERALIZE 			cph_highway -> cph_highway_output 

WITH ID 			ogc_fid
WITH GEOMETRY		wkb_geometry
WITH OTHER			type, name, lanes, oneway

AT  				15 ZOOM LEVELS

RANK BY 			st_length(wkb_geometry)

PARTITION BY 		type -- this is a column in cph_highway

SUBJECT TO 
	 PROXIMITY 		5 -- pixels
```

With input parameters CURRENT_Z and D: Update temporary table *_records_to_delete*:

```sql
CREATE TEMPORARY TABLE IF NOT EXISTS _records_to_delete(ogc_fid int);

INSERT INTO _records_to_delete
SELECT
    -- Delete lowest ranking record
	CASE WHEN l._rank <= r._rank THEN l.ogc_fid ELSE r.ogc_fid
FROM 
	cph_highway_output l JOIN
	cph_highway_output r
ON 
	l.ogc_fid < r.ogc_fid
AND l._partition = r._partition
AND l._tile_level = CURRENT_Z
AND r._tile_level = CURRENT_Z
AND ST_DWithin(l.wkb_geometry, r.wkb_geometry, ST_ResZ(CURRENT_Z) * D)
```