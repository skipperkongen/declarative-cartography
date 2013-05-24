# Evaluating proximity constraint

Problem: Make sure no two records are too close to each other (in pixels).

As for all constraints, the aim is to populate the temporary *_conflicts* table.

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

With input parameters CURRENT_Z and DISTANCE, update temporary table *_conflicts*:

```sql
INSERT INTO _conflicts
SELECT ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id, unnest(array[l.ogc_fid, r.ogc_fid]) AS record_id, unnest(array[l._rank, r._rank]) AS _rank
FROM 
	cph_highway_output l JOIN
	cph_highway_output r
ON 
	l.ogc_fid < r.ogc_fid
AND l._partition = r._partition
AND l._tile_level = 15
AND r._tile_level = 15
AND ST_DWithin(l.wkb_geometry, r.wkb_geometry, 10)
```









