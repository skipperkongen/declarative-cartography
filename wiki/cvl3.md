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
MERGE PARTITIONS	{(value, ...) AS {text} AND (value, ...) AS {text} AND (*)}

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