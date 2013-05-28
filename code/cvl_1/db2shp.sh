#!/bin/bash

ogr2ogr $1.shp -t_srs "epsg:4326" PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -sql "select * from $1"
zip _$1 $1.*
rm $1.*
mv _$1.zip $1.zip
