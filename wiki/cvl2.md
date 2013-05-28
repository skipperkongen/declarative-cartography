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
PARTITION BY 		{expression} -- e.g. a column name
```

New *PARTITION BY*:

```cvl
PARTITION BY        {expression} -- e.g. a column name
MERGE PARTITIONS    
					({value_1}, ...) AS {partition_value}
AND 				({value_2}) AS {partition_value}
AND					* AS {partition_value}
```

Optionally merge remaining partitions using a * (if omitted, remaiming partitions are kept as "singleton" partitions):

```cvl
PARTITION BY        {expression} -- e.g. a column name
MERGE PARTITIONS    
					({value_1}, ...) AS {partition_value}
AND 				({value_2}) AS {partition_value}
AND					* AS {partition_value}
```

## New FORCE LEVELS

New *FORCE LEVELS*:

```cvl
FORCE LEVELS
					{zoomlevel} TO {zoomlevel} FOR {partition_value}
AND					{zoomlevel} TO {zoomlevel} FOR {partition_value}					
AND 				...
```

Partitions that are mentioned in a FORCE LEVEL clause will not be evaluated using the constraints.

## Example

```cvl
GENERALIZE          cph_osm_highway -> cph_osm_highway_generalized

WITH ID             ogc_fid
WITH GEOMETRY       wkb_geometry
WITH OTHER          name, type, lanes, oneway

AT                  16 ZOOM LEVELS

-- no RANK BY

PARTITION BY        type
MERGE PARTITIONS    
					(motorway, motorway_link, primary) AS big_ones
AND 				(secondary) AS small_ones
AND					* AS the_rest

FORCE LEVELS
                    9 TO 15 FOR big_ones
AND                 12 TO 15 FOR small_ones
AND					16 TO 16 FOR the_rest 

TRANSFORM BY
    SIMPLIFY
```

