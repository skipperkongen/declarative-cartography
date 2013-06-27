# Data for CVL

## Loading data into database

```
tar xjvf name_of_file.tar.bz2
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=foo password=bar dbname=baz" -t_srs "epsg:3857" name_of_file.shp
```

