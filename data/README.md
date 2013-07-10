# Data for CVL

Unpack data in this dir

```
tar xjvf *.tar.bz2
```

Download other data. Some of it is too large for Github.

```
TODO
```

Load data into DB

```
/usr/local/bin/ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -t_srs "epsg:3857" *.shp
``` 

