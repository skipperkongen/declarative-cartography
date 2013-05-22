# CVL view of input

Given a [CVL query] create a view to use during generalization process as follows:

```sql
CREATE VIEW cvl_input_MD5HashOfInputClause AS
SELECT 
	*, 
	partition_by_clause as cvl_partition, 
	rank_by_clause as cvl_rank
FROM 
	input_clause;
```

During the last steps of the generalization process the view is deleted again:

```sql
DROP VIEW IF EXISTS cvl_input_MD5HashOfInputClause;
```

In general, temporary things are prefixed with *cvl_*.