#!/bin/sh

echo "Running experiments"

# truncate log-file (BASH)
touch /tmp/cvl.log
cat /dev/null >| /tmp/cvl.log

./ex1_bound.py > cvl.sql
psql -q -d cvl_paper -f cvl.sql

./ex1_lp.py > cvl.sql
psql -q -d cvl_paper -f cvl.sql

./ex1_heuristic.py > cvl.sql
psql -q -d cvl_paper -f cvl.sql
