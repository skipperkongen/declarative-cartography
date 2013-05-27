# Manual reduction of partitions

The OSM highway dataset did not do too well. I think it is because there are too many partitions.

## Manually create 5 groups from original partitions (used *type* column):

Make a copy of original table and add a column for the cluster-id:

```sql
CREATE TABLE cph_highway_copy AS
SELECT * FROM cph_highway;
-- 357 ms execution time
ALTER TABLE cph_highway_copy ADD COLUMN _cluster_id text;
```

Order original partitions by AVG(ST_Length(wkb_geometry))

```sql
SELECT ROW_NUMBER() OVER (ORDER BY AVG(ST_Length(wkb_geometry))) as r, type, AVG(ST_Length(wkb_geometry)) FROM cph_highway_copy GROUP BY type
```

Result:

```
1       "footpath"          25.6824500902169
2       "elevator"          27.3465194286262
3       "tertiary_link"     28.8113510353613
4       "steps"             28.8876872565808
5       "parking_aisle"     53.9869841632674
6       "mini_roundabout"   93.7705017344146
7       "driveway"          121.87410492716
8       "pedestrian"        196.214442364432
9       "living_street"     245.168732950111
10      "footway"           249.456252785017
11      "proposed"          255.159812458839
12      "ps"                281.594661792331
13      "service"           295.283431383635
14      "secondary_link"    318.094340460757
15      "residential"       406.859343477658
16      "path"              425.772542467599
17      "raceway"           435.9228571857
18      "primary_link"      450.048825106736
19      "cycleway"          470.034366325362
20      "road"              477.242744426391
21      "motorway_link"     649.449489913686
22      "trunk_link"        703.365117217018
23      "track"             877.861016730898
24      "bridleway"         896.280894536543
25      "tertiary"          1027.22141743728
26      "primary"           1126.55680436444
27      "unclassified"      1182.76865261217
28      "trunk"             1427.35117104817
29      "construction"      1607.53453300145
30      "secondary"         1677.87023412163
31      "motorway"          1965.85616116289
32      ""                  26235.8451055314
```