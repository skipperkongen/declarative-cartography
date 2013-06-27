#!/bin/sh

echo "Running experiments"

# truncate log-file (BASH)
touch /tmp/cvl.log
cat /dev/null >| /tmp/cvl.log

for experiment in *.py
do
    echo "Running $experiment"
    "./$experiment" > cvl.sql
    psql -q -d cvl_paper -f cvl.sql
done
