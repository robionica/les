#!/bin/sh

echo "Recursively removing *.pyc files from"
pwd
find ./ -name '*.pyc' -exec rm '{}' \; -print -or -name ".*.pyc" -exec rm {} \; -print
