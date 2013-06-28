#!/bin/sh

echo "Running experiments"

COMP_NAME="macbook"
mkdir "../results/traces/$COMP_NAME"

# truncate log-file (BASH)
touch /tmp/cvl.log
cat /dev/null >| /tmp/cvl.log

echo "Running experiment $1"
"./$1" > cvl.sql
psql -q -d cvl_paper -f cvl.sql
mv /tmp/cvl.log > "../results/traces/$COMP_NAME/$1.log"
