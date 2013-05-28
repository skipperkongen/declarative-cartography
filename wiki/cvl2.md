# CVL 2

Based on experience with implementing CVL, I have learned that finding good groupings of data is crucial. The assumption (which does not hold) was that there is a strong connection between how globally relevant a group of records is, and how many records there are. For example the assumption was that there are only few motorways (which should be displayed globally), and many residential streets (which should be displayed locally). The connection is not strong enough to generate an appropriate map. 

## The data is full of surprises

### Surprise 1: Rare does not mean global, common does not mean local

I had assumed that there would be a correspondance between the size of partitions, and the global relevance of records the partition.

> Assumption: There are fewer motorways than driveways in the data

That assumption might hold for the real world, but it does not hold for (OSM) data. That could be because driveways are less likely to be digitized than motorways. It would be interesting to see how the case is for public government curated data.

For example in the OSM data for Copenhagen, there are roughly 300 motorway records, while there is only three 'driveway' records

This can be seen from the following SQL select:

```sql
select type, count(*) from cph_highway group by type order by count(*);
```

Which produces the following output:

```
"mini_roundabout";1
"ps";1
"footpath";1
"elevator";1
"parking_aisle";1
"tertiary_link";2
"driveway";3
"secondary_link";4
"";9
"raceway";9
"proposed";12
"road";24
"primary_link";24
"construction";28
"trunk_link";46
"trunk";60
"bridleway";63
"living_street";140
"pedestrian";204
"motorway";304
"motorway_link";361
"primary";383
"steps";589
"secondary";607
"tertiary";1984
"track";2161
"unclassified";2941
"cycleway";4150
"path";4419
"footway";5860
"service";7216
"residential";26204
```

### Surprise 2: The geometric length of records is not very strongly correlated to street class significance

I tried ordering street classes by average geometric length.

```sql
SELECT 
	ROW_NUMBER() OVER (ORDER BY AVG(ST_Length(wkb_geometry))) as r, 
	type, AVG(ST_Length(wkb_geometry)) 
	FROM cph_highway 
	GROUP BY type;
```

While *motorways* are the second longest category (on par with my intuition), the longest (by far) is actually the *non-categorized* category (null category). Also, *secondary* streets are on average 50% longer than *primary* streets.

See the result below

```sql
1;"footpath";			25.6824500902169
2;"elevator";			27.3465194286262
3;"tertiary_link";		28.8113510353613
4;"steps";				28.8876872565808 
5;"parking_aisle";		53.9869841632674 
6;"mini_roundabout";	93.7705017344146 <-- big jump 
7;"driveway";			121.87410492716  <-- big jump 
8;"pedestrian";			196.214442364432
9;"living_street";		245.168732950111 
10;"footway";			249.456252785017
11;"proposed";			255.159812458839
12;"ps";				281.594661792331
13;"service";			295.283431383635
14;"secondary_link";	318.094340460757 
15;"residential";		406.859343477658
16;"path";				425.772542467599
17;"raceway";			435.9228571857
18;"primary_link";		450.048825106736
19;"cycleway";			470.034366325362
20;"road";				477.242744426391 <-- big jump
21;"motorway_link";		649.449489913686 
22;"trunk_link";		703.365117217018 
23;"track";				877.861016730898
24;"bridleway";			896.280894536543
25;"tertiary";			1027.22141743728
26;"primary";			1126.55680436444
27;"unclassified";		1182.76865261217 <-- big jump
28;"trunk";				1427.35117104817
29;"construction";		1607.53453300145
30;"secondary";			1677.87023412163 <-- secondary roads are longer than primary
31;"motorway";			1965.85616116289
32;"";					26235.8451055314
```

### Conclusion

In the case of OSM data, the size of a street category is a very bad predictor of how globally relevant the category is. The AVG geometric length of records in a street category is a better predictor, but not perfectly intuitive. 

This means there is a for making better grouping of records. There are two obvious ways to go: Better algorithm (hard to get right) and more verbose user input (configuration hell). Probably the best approach is somewhere in the middle.

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

