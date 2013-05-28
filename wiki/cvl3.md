# CVL 3

Brian mentioned that a cartographer often knows which zoom-levels a given class of records should be shown at. 

CVL 3 contains a directive FORCE LEVELS for this, plus the MERGE PARTITIONS introduced in CVL 2.

```cvl
GENERALIZE 			{input} -> {output} 

WITH ID 			{column name}
WITH GEOMETRY		{column name}
WITH OTHER			{column name, column name, column name, ...}

AT  				{Z} ZOOM LEVELS

RANK BY 			{float-valued expression}

PARTITION BY 		{expression}
MERGE PARTITIONS	{(value, ...), (value, ...), (*)}

SUBJECT TO 
	 PROXIMITY 		{d} 
THEN CELLBOUND 		{K} 
THEN ALLORNOTHING

FORCE LEVELS
					{N} - {N} FOR {partition-value}
AND 				{N} - {N} FOR {partition-value}
AND 				...

TRANSFORM BY
	SIMPLIFY
```

The idea is that constraints are not evaluated for partitions mentioned in the FORCE LEVELS clause.