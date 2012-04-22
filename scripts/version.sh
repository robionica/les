#!/bin/sh

vf=./include/les/version.h

major=`grep LES_MAJOR_VERSION $vf |head -1 | awk '{print $3}'`
minor=`grep LES_MINOR_VERSION $vf | head -1 | awk '{print $3}'`
patch=`grep LES_PATCH_VERSION $vf | head -1 | awk '{print $3}'`
tail=`grep LES_VERSION_TAIL $vf | head -1 | awk '{print $3}'`

if [ x$tail = xrelease ] ; then
 echo -n "${major}_${minor}_${patch}"
else
 echo -n "${major}_${minor}_${patch}_${tail}"
fi

