# CVL 2

Based on experience with implementing CVL, I have learned that finding good groupings of data is crucial. The assumption (which does not hold) was that there is a strong connection between how globally relevant a group of records is, and how many records there are. For example the assumption was that there are only few motorways (which should be displayed globally), and many residential streets (which should be displayed locally). The connection is not strong enough to generate an appropriate map. 

## Modified CVL language

To get better grouping facilities, the CVL language is modified. Here are some ideas

### More automation

```cvl
GENERALIZE 			{input} -> {output} 

WITH ID 			{column name}
WITH GEOMETRY		{column name}
WITH OTHER			{column name, column name, column name, ...}

AT  				{Z} ZOOM LEVELS

RANK BY 			{float-valued expression}

PARTITION INTO 5 GROUPS BY METRIC
 					{expression} <-- e.g. AVG(ST_length)

SUBJECT TO 
	 PROXIMITY 		{d} 
THEN CELLBOUND 		{K} 
THEN ALLORNOTHING 

TRANSFORM BY
	SIMPLIFY
```

### More user input

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

TRANSFORM BY
	SIMPLIFY
```

I prefer this specification.
