# Using the LP-solver with a Postgres database

Assuming that CVL has run in "export mode" so that a multi-scale conflicts table was written after the CVL transaction, this is how to run the LP solver using that table.

Assuming the table is *geodata_export_conflicts*, run the following:

```
./lpbuilder geodata_export_conflicts
./lpsolver hittingset.lp
```

Copy LP solution into PostgreSQL:

```sql
COPY lp_solution FROM '/tmp/records_to_delete.sol' CSV HEADER;
```
