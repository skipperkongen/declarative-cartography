# Is LP solver correct?

Instance:

```sql
CREATE TABLE _conflicts (conflict_id text, cvl_id bigint, cvl_rank float, min_hits integer);

insert into _conflicts values('A', 1, 0.5, 1);
insert into _conflicts values('A', 2, 1.5, 1);

select CVL_LP('_conflicts');
```

Looks like it...

```
b:
[ 0.00e+00]
[ 0.00e+00]
[ 1.00e+00]
[ 1.00e+00]
[-1.00e+00]

c:
[ 5.00e-01]
[ 1.50e+00]

A:
[-1.00e+00     0    ]
[    0     -1.00e+00]
[ 1.00e+00     0    ]
[    0      1.00e+00]
[-1.00e+00 -1.00e+00]

Result:
1 got 0.999999999269
2 got 1.49987569064e-09
```

