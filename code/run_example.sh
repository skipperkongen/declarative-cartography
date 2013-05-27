#!/bin/sh

echo "Running example $1"
./example$1.py | pbcopy
echo "Output copied to clip-board"