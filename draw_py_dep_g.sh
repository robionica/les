#!/bin/bash
#
# Copyright (c) 2013 Oleksandr Sviridenko
#
# Please install modulegraph and altgraph.
#
# USAGE: ./draw_py_dep_g.sh src/main/python/les/model/model.py g.png

PYTHON=python
if [ $# -gt 2 ]; then
    PYTHON=$3
fi
EXCLUDE_MODULES=(sympy numpy scipy gzip os subprocess sys logging unittest
    collections itertools types)
EXCLUDE_STRING="-x __future__"
for mod in ${EXCLUDE_MODULES[@]}
do
    EXCLUDE_STRING+=" -x $mod"
done

$PYTHON -mmodulegraph $EXCLUDE_STRING -g $1 | dot -T png -o $2
