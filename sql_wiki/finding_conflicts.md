# Finding conflicting K-sets of records

Using OpenStreetMap streets in the Copenhagen region (count=57,812)as example. There are  (GIST index on wkb_geometry).

Let's try computing conflicts for a K=4 constraint and a constraint condition being ST_Dwithin(a.wkb_geometry, b.wkb_geometry, 100)

This can be achieved with a K-way join using

* K-1 "identical type" clauses (only compare motorways with motorways etc.)
* K-1 "different and monotonically increasing id" clauses
* O(n^2) constraint clauses, comparing using ST_Dwithin

```sql
SELECT r1.ogc_fid as id_1, r2.ogc_fid as id_2, r3.ogc_fid as id_3, r4.ogc_fid as id_4
FROM cph_highway r1, cph_highway r2, cph_highway r3, cph_highway r4
WHERE r1.type = r2.type
AND r2.type = r3.type
AND r3.type = r4.type
AND r1.ogc_fid < r2.ogc_fid
AND r2.ogc_fid < r3.ogc_fid
AND r3.ogc_fid < r4.ogc_fid
AND st_dwithin(r1.wkb_geometry, r2.wkb_geometry, 100)
AND st_dwithin(r1.wkb_geometry, r3.wkb_geometry, 100)
AND st_dwithin(r1.wkb_geometry, r4.wkb_geometry, 100)
AND st_dwithin(r2.wkb_geometry, r3.wkb_geometry, 100)
AND st_dwithin(r2.wkb_geometry, r4.wkb_geometry, 100)
AND st_dwithin(r3.wkb_geometry, r4.wkb_geometry, 100)
-- Total query runtime: 41512 ms.
-- 61,818 rows retrieved.
```sql

Repeating the query with K=8:

```sql
SELECT 
	r1.ogc_fid as id_1, 
	r2.ogc_fid as id_2, 
	r3.ogc_fid as id_3, 
	r4.ogc_fid as id_4,
	r1.ogc_fid as id_5, 
	r2.ogc_fid as id_6, 
	r3.ogc_fid as id_7, 
	r4.ogc_fid as id_8	
FROM 
	cph_highway r1, 
	cph_highway r2, 
	cph_highway r3, 
	cph_highway r4,
	cph_highway r5, 
	cph_highway r6, 
	cph_highway r7, 
	cph_highway r8
WHERE 
	r1.type = r2.type
	AND r2.type = r3.type
	AND r3.type = r4.type
	AND r4.type = r5.type
	AND r5.type = r6.type
	AND r6.type = r7.type
	AND r7.type = r8.type	
	
	AND r1.ogc_fid < r2.ogc_fid
	AND r2.ogc_fid < r3.ogc_fid
	AND r3.ogc_fid < r4.ogc_fid
	AND r4.ogc_fid < r5.ogc_fid
	AND r5.ogc_fid < r6.ogc_fid
	AND r6.ogc_fid < r7.ogc_fid
	AND r7.ogc_fid < r8.ogc_fid
			
	AND st_dwithin(r1.wkb_geometry, r2.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r3.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r8.wkb_geometry, 100)

	AND st_dwithin(r2.wkb_geometry, r3.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r8.wkb_geometry, 100)
	
	AND st_dwithin(r3.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r8.wkb_geometry, 100)
	
	AND st_dwithin(r4.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r8.wkb_geometry, 100)
	
	AND st_dwithin(r5.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r8.wkb_geometry, 100)
	
	AND st_dwithin(r6.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r8.wkb_geometry, 100)
	
	AND st_dwithin(r7.wkb_geometry, r8.wkb_geometry, 100)
```sql
