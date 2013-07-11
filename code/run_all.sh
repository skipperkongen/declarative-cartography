#!/bin/sh

echo "Running experiments"

cat /proc/meminfo > ../results/meta/meminfo.txt
cat /proc/cpuinfo > ../results/meta/cpuinfo.txt

git add ../results/meta/meminfo.txt
git add ../results/meta/cpuinfo.txt

./run.sh test_performance.py
./run.sh test_quality.py
./run.sh test_scalability.py

