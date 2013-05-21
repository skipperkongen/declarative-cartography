# Using Grid

Use [ST_Cellify]() to compute grid cells for a geometry. Then convert point to some kind of hash (see below). Finally, for each hash, count records and check if more than K.

Use [ST_GeoHash](http://postgis.refractions.net/documentation/manual-svn/ST_GeoHash.html) to compute GeoHash of point.:

```sql
SELECT ST_GeoHash(ST_SetSRID(ST_MakePoint(-126,48),4326));
```

The documentation says that geohash is only valid for lat/long coordinates (epsg:4326), but since hash is only used as a unique key, it should work fine with epsg:3857 as well.