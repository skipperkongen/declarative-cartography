# Data for CVL

Unpack data
-----------
tar xjvf *.tar.bz2


Load data into DB
-----------------
/usr/local/bin/ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -t_srs "epsg:3857" *.shp


