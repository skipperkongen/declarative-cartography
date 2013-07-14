#!/bin/sh

echo "Running experiments"

cat /proc/meminfo > ../results/meta/meminfo.txt
cat /proc/cpuinfo > ../results/meta/cpuinfo.txt

git add ../results/meta/meminfo.txt
git add ../results/meta/cpuinfo.txt

./run.sh test_basic.py
./run.sh test_scalability.py
./run.sh test_burnout.py


