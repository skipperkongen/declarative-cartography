#!/bin/sh

ogr2ogr -f '"PostgreSQL" PG:'host=localhost user=' + $1 + 'dbname=cvl_paper' -t_srs 'epsg:3857' $2


