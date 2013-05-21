# Finding conflicts between sets of K records using K-way joins

Using OpenStreetMap streets in the Copenhagen region (57,812 records) as example. There is a GIST index on wkb_geometry.

Let's try computing conflicts for a K=4 constraint and a constraint condition being ST_Dwithin(a.wkb_geometry, b.wkb_geometry, 100)

## K=4, distance 100 meters, 42 seconds

This can be achieved with a K-way join using

* K-1 "identical type" clauses (only compare motorways with motorways etc.)
* K-1 "different and monotonically increasing id" clauses
* O(n^2) constraint clauses, comparing using ST_Dwithin

```sql
SELECT 
	r1.ogc_fid as id_1, 
	r2.ogc_fid as id_2, 
	r3.ogc_fid as id_3, 
	r4.ogc_fid as id_4
FROM 
	cph_highway r1, 
	cph_highway r2, 
	cph_highway r3, 
	cph_highway r4
WHERE 
	r1.type = r2.type
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
```

## K=8, distance 100 meters, 143 seconds

Repeating the query with K=8, i.e. double the K:

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
-- Total query runtime: 143002 ms.
-- 99,608 rows retrieved.	
```

This query retrieves 50% more rows (conflicts) and takes 3.5 times longer to compute. This it not too terrible actually. Not sure whether the quadratic number of where clauses will eventually kill the query completely? Let's try

## K=16, distance 100 meters, <1200 seconds

Double K from 8 to 16?

```sql
SELECT 
	r1.ogc_fid as id_1, 
	r2.ogc_fid as id_2, 
	r3.ogc_fid as id_3, 
	r4.ogc_fid as id_4,
	r1.ogc_fid as id_5, 
	r2.ogc_fid as id_6, 
	r3.ogc_fid as id_7, 
	r4.ogc_fid as id_8,
	r1.ogc_fid as id_9, 
	r2.ogc_fid as id_10, 
	r3.ogc_fid as id_11, 
	r4.ogc_fid as id_12,
	r1.ogc_fid as id_13, 
	r2.ogc_fid as id_14, 
	r3.ogc_fid as id_15, 
	r4.ogc_fid as id_16	
FROM 
	cph_highway r1, 
	cph_highway r2, 
	cph_highway r3, 
	cph_highway r4,
	cph_highway r5, 
	cph_highway r6, 
	cph_highway r7, 
	cph_highway r8,
	cph_highway r9, 
	cph_highway r10, 
	cph_highway r11, 
	cph_highway r12,
	cph_highway r13, 
	cph_highway r14, 
	cph_highway r15, 
	cph_highway r16
WHERE 
	r1.type = r2.type
	AND r2.type = r3.type
	AND r3.type = r4.type
	AND r4.type = r5.type
	AND r5.type = r6.type
	AND r6.type = r7.type
	AND r7.type = r8.type
	AND r9.type = r10.type
	AND r10.type = r11.type
	AND r11.type = r12.type
	AND r12.type = r13.type
	AND r13.type = r14.type
	AND r14.type = r15.type
	AND r15.type = r16.type	
	
	AND r1.ogc_fid < r2.ogc_fid
	AND r2.ogc_fid < r3.ogc_fid
	AND r3.ogc_fid < r4.ogc_fid
	AND r4.ogc_fid < r5.ogc_fid
	AND r5.ogc_fid < r6.ogc_fid
	AND r6.ogc_fid < r7.ogc_fid
	AND r7.ogc_fid < r8.ogc_fid
	AND r9.ogc_fid < r2.ogc_fid
	AND r10.ogc_fid < r11.ogc_fid
	AND r11.ogc_fid < r12.ogc_fid
	AND r12.ogc_fid < r13.ogc_fid
	AND r13.ogc_fid < r14.ogc_fid
	AND r14.ogc_fid < r15.ogc_fid
	AND r15.ogc_fid < r16.ogc_fid
			
	AND st_dwithin(r1.wkb_geometry, r2.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r3.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r1.wkb_geometry, r15.wkb_geometry, 100)	
	AND st_dwithin(r1.wkb_geometry, r16.wkb_geometry, 100)		

	AND st_dwithin(r2.wkb_geometry, r3.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r2.wkb_geometry, r15.wkb_geometry, 100)	
	AND st_dwithin(r2.wkb_geometry, r16.wkb_geometry, 100)		
	
	AND st_dwithin(r3.wkb_geometry, r4.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r3.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r4.wkb_geometry, r5.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r12.wkb_geometry, 100)	
	AND st_dwithin(r4.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r4.wkb_geometry, r16.wkb_geometry, 100)	
	
	AND st_dwithin(r5.wkb_geometry, r6.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r14.wkb_geometry, 100)	
	AND st_dwithin(r5.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r5.wkb_geometry, r16.wkb_geometry, 100)	
	
	AND st_dwithin(r6.wkb_geometry, r7.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r10.wkb_geometry, 100)	
	AND st_dwithin(r6.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r14.wkb_geometry, 100)	
	AND st_dwithin(r6.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r6.wkb_geometry, r16.wkb_geometry, 100)

	AND st_dwithin(r7.wkb_geometry, r8.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r7.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r8.wkb_geometry, r9.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r8.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r9.wkb_geometry, r10.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r11.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r9.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r10.wkb_geometry, r11.wkb_geometry, 100)	
	AND st_dwithin(r10.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r10.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r10.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r10.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r10.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r11.wkb_geometry, r12.wkb_geometry, 100)
	AND st_dwithin(r11.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r11.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r11.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r11.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r12.wkb_geometry, r13.wkb_geometry, 100)
	AND st_dwithin(r12.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r12.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r12.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r13.wkb_geometry, r14.wkb_geometry, 100)
	AND st_dwithin(r13.wkb_geometry, r15.wkb_geometry, 100)
	AND st_dwithin(r13.wkb_geometry, r16.wkb_geometry, 100)
	
	AND st_dwithin(r14.wkb_geometry, r15.wkb_geometry, 100)					
	AND st_dwithin(r14.wkb_geometry, r16.wkb_geometry, 100)					
	
	AND st_dwithin(r15.wkb_geometry, r16.wkb_geometry, 100)
-- 
```

## Conclusion

This approach does not scale very well. It is feasible only for small record sets and small K.