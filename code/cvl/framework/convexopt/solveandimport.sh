#!/bin/sh
./lpbuilder.py "$1_export_conflicts"
./lpsolver.py hittingset.lp
mv records_to_delete.sol /tmp

psql -d cvl_paper --command 'DROP TABLE IF EXISTS lp_solution;'
psql -d cvl_paper --command 'CREATE TABLE lp_solution (zoom integer, record_id text, record_rank double precision, lp_value double precision);' 
psql -d cvl_paper --command "COPY lp_solution FROM '/tmp/records_to_delete.sol' CSV HEADER;"
