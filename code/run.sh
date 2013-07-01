#!/bin/sh

echo "Running experiments"

COMP_NAME="macbook"
DIRECTORY="../results/traces/$COMP_NAME"
if [ ! -d "$DIRECTORY" ]; then
  mkdir "$DIRECTORY"
fi

# truncate log-file (BASH)
touch /tmp/cvl.log
cat /dev/null >| /tmp/cvl.log

echo "Running experiment $1"
"./$1" > cvl.sql
psql -q -d cvl_paper -f cvl.sql

mv /tmp/cvl.log "$DIRECTORY/$1.log"
git add "$DIRECTORY/$1.log"
#   git commit -a -m 'commiting experiment'