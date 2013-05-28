# CVL 2

Based on experience with implementing CVL, I have learned that finding good groupings of data is crucial. The assumption (which does not hold) was that there is a strong connection between how globally relevant a group of records is, and how many records there are. For example the assumption was that there are only few motorways (which should be displayed globally), and many residential streets (which should be displayed locally). The connection is not strong enough to generate an appropriate map. 

## Extending PARTITION BY

To get better grouping facilities, the CVL language is modified. Here are some ideas that were considered.

### More automation (not chosen)

A more automatic approach to partitioning could be to have a clustering algorithm create the partitions.

```cvl
PARTITION INTO 5 GROUPS BY METRIC
                    {expression} <-- e.g. AVG(ST_length)
```

I've chosen not to do this at this point of time for CVL 2

### More user input (chosen)

Another approach (the one I've chosen for CVL 2) is to have the user specify how to partition using an extended *PARTITION BY* clause.

Old *PARTITION BY*:

```cvl
PARTITION BY        {expression} -- e.g. a column name
```

New *PARTITION BY*:

```cvl
PARTITION BY        {expression} -- e.g. a column name
MERGE PARTITIONS    
                    ({value_1}, ...) AS {partition_value}
AND                 ({value_2}) AS {partition_value}
AND                 * AS {partition_value}
```

Optionally merge remaining partitions using a * (if omitted, remaiming partitions are kept as "singleton" partitions):

```cvl
PARTITION BY        {expression} -- e.g. a column name
MERGE PARTITIONS    
                    ({partition_value}, ...) AS {partition_value}
AND                 ({partition_value}) AS {partition_value}
AND                 * AS {partition_value}
```

## New FORCE MIN LEVEL

New *FORCE MIN LEVEL*:

```cvl
FORCE MIN LEVEL
                    {zoomlevel} FOR {partition_value}
AND                 {zoomlevel} FOR {partition_value}                   
AND                 ...
```

Partitions that are mentioned in a FORCE MIN LEVEL clause will not be evaluated using the constraints.

## Full syntax

All clauses:

```cvl
GENERALIZE          {relation name} TO {relation name}

WITH ID             {column name}
WITH GEOMETRY       {column name}
WITH OTHER          {column name, column name, column name, ...}

AT                  {positive integer} ZOOM LEVELS

RANK BY             {float expression}

PARTITION BY        {expression} -- e.g. column name or function call
MERGE PARTITIONS    
                    {expression}, {expression} AS {expression} -- multiple
AND                 {expression} AS {expression} -- singleton
AND                 * AS {expression} -- the rest

FORCE MIN LEVEL
                    {positive integer} FOR {expression}
AND                 {positive integer} FOR {expression}

SUBJECT TO 
     {constraint}   {float expression} 
THEN {constraint}   {float expression}
THEN {constraint}

TRANSFORM BY
    {operation}
```

Mandatory clauses:

```cvl
GENERALIZE          {relation name} TO {relation name}

WITH ID             {column name}
WITH GEOMETRY       {column name}

AT                  {positive integer} ZOOM LEVELS
```

Defaults used for optional clauses (not all have defaults):

```cvl
WITH OTHER          None

RANK BY             1

PARTITION BY        1

MERGE PARTITIONS	None

SUBJECT TO			None

FORCE MIN LEVEL		None

TRANSFORM BY        'SIMPLIFY'
```

## Examples

Implementing Brian's use case:

```cvl
GENERALIZE          denmark_highway TO denmark_highway_generalized

WITH ID             ogc_fid
WITH GEOMETRY       wkb_geometry
WITH OTHER          name, type, lanes, oneway

AT                  16 ZOOM LEVELS

PARTITION BY        type

MERGE PARTITIONS    
                    (motorway, motorway_link, primary) AS big_ones
AND                 (secondary) AS small_ones
AND                 * AS the_rest

FORCE MIN LEVEL
                    9 FOR big_ones
AND                 12 FOR small_ones
AND                 16 FOR the_rest -- meaning don't show 

TRANSFORM BY
    SIMPLIFY
```

