#!/bin/sh

ogr2ogr cph_highway_thin.shp -t_srs "epsg:4326" PG:"host=localhost user=postgres password=postgres dbname=cvl_paper" -sql "select * from cph_highway_output where wkb_geometry && (select st_buffer(st_extent(wkb_geometry),10000) from cph_highway_output where name in ('Bagsværd Hovedgade', 'Amagerbrogade'))"

zip _cph_highway_thin.zip cph_osm.*
rm cph_highway_thin.*
mv _cph_highway_thin.zip _cph_highway_thin.zip
