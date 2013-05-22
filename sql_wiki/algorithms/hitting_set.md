# Hitting Set Problem in SQL

Hitting Set Problem is analogous with [Set Cover problem](http://en.wikipedia.org/wiki/Set_cover_problem).

## Table schema for instance

Table schema for instances:

* *set_id* INTEGER
* *record_id* INTEGER|TEXT
* *record_rank* FLOAT

## Creating a test instance

Test instance with roughly 250K rows:

```sql
CREATE TABLE hitting_set AS  
SELECT set_id, r.record_id, r.record_rank 
FROM generate_series(1,500) set_id
JOIN (SELECT generate_series(1,10000) as record_id, random() as record_rank) r
ON random() < 0.05 -- probability of record i being in set j
ORDER BY set_id, r.record_id
-- roughly 250K records
```

Snippet of data:

```
+--------+-----------+-------------+
| set_id | record_id | record_rank |
+--------+-----------+-------------+  
|    403 |      6239 |   0.0546426 |
|    403 |      6247 |   0.4384571 |
|    403 |      6262 |   0.7345629 |
|    127 |      6269 |   0.1117468 |
|    127 |      6279 |   0.1856906 |
|    127 |      6282 |   0.7433926 |
|    ... |       ... |         ... | 
+--------+-----------+-------------+
```

## Algorithm 1: Heuristic

Heuristic for Hitting Set

```sql
SELECT h.set_id, h.record_id, h.record_rank 
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY set_id ORDER BY record_rank) AS r,
    t.*
    FROM hitting_set t) h
WHERE h.r = 1
-- Total query runtime: 568 ms.
-- 500 rows retrieved.
```

### Quality evaluation

How many times each set is covered on average:

```sql
WITH solution AS 
(SELECT h.set_id, h.record_id, h.record_rank 
FROM (SELECT ROW_NUMBER() OVER (PARTITION BY set_id ORDER BY record_rank) AS r,
    t.*
    FROM hitting_set t) h
WHERE h.r = 1)

SELECT avg(x.count) as avg_times_covered FROM 
(SELECT r.set_id, count(*) as count
FROM
solution s JOIN hitting_set r
ON s.record_id = r.record_id
GROUP BY r.set_id
ORDER BY r.set_id) x
-- Total query runtime: 749 ms.
```

Result:

```
+-------------------+
| avg_times_covered |
+-------------------+
|             26.41 |
+-------------------+
```

Hmm, 26 times seems quite bad... but I don't know what the optimum is. The solution selects 500 records out of 10000 possible. The average set size is ~500. So maybe 26 out of 500 is not too bad (it's ~5% of the elements in a set). This is likely a property of all the ranks being unique... This might be an argument for randomizing the ranks a little (if they are very likely to be the same), to make them unique!


## Algorithm 2: Approximation algorithm for Set Cover (Vazirani)

TODO: A bit tricky to implement in SQL. Next up if Heuristic proves too bad.