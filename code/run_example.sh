#!/bin/sh

echo "Running example $1"
./$1.py | pbcopy
echo "Output copied to clip-board"