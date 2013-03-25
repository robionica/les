#!/bin/sh

echo "Remove backup files from"
pwd
find ./ -name '*~' -exec rm '{}' \; -print -or -name ".*~" -exec rm {} \; -print
