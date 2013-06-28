# Modifying datasets for scalability test

```sql
CREATE TABLE foo_scal AS
SELECT ROW_NUMBER() OVER (ORDER BY ST_XMin(wkb_geometry)) AS x_order, * FROM foo;

CREATE UNIQUE INDEX foo_scal_idx ON foo_scal(x_order);
```