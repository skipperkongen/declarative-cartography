# Finding (pairs of) records that are close together

The general structure of proximity query (spatial join):

```sql
SELECT 
	l.id,
	r.id
FROM 
	table_name l JOIN
	table_name r
ON 
	l.id < r.id
AND ST_DWithin(l.wkb_geometry, r.wkb_geometry, distance)
```

## Running time on different datasets

Example query for US Airports:

```sql
SELECT 
	l.ogc_fid,
	r.ogc_fid
FROM 
	us_geocommons_airports l JOIN
	us_geocommons_airports r
ON 
	l.ogc_fid < r.ogc_fid
AND ST_DWithin(l.wkb_geometry, r.wkb_geometry, 1000)
-- Total query runtime: 541 ms.
-- 63 rows retrieved.
```

Performance on different datasets:

<table>
	<tr><th>Distance</th><th>Record set</th><th>Record set size</th><th>Geometry type</th><th>#Matched</th><th>Milliseconds</th></tr>
	<tr><td>1000 m</td><td>us_geocommons_airports</td><td>13,617</td><td>Points</td><td>63</td><td>541 ms</td></tr>
	<tr><td>1000 m</td><td>cph_highway</td><td>57,812</td><td>Linestrings</td><td>2,886,377</td><td>28,023 ms</td></tr>
	<tr><td>50 m</td><td>cph_highway</td><td>57,812</td><td>Linestrings</td><td>144,326</td><td>9,025 ms</td></tr>
</table>

Performance is closely related to number of matched records. So, it depends on whether 1000m is a lot or a little for the given dataset.

## Transformation to general conflict set form

The table schema for an instance of hitting set is (*set_id* INTEGER, *record_id* INTEGER).



## Conclusion

Performs well. Scales ok (could be better, joins on some datasets are going to be expensive).