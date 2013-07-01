#!/bin/sh

echo "Running experiments"

for exfile in *.py
do
    ./run.sh "$exfile"
done
