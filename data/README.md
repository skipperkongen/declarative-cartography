# Data for CVL

Download data from http://skipperkongen.dk/geodata/

## Loading data into database

```
unzip name_of_file.zip
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=foo password=bar dbname=baz" -t_srs "epsg:3857" name_of_file.shp
```

