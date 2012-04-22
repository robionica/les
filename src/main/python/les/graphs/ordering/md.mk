#
# Copyright (c) 2012 Alexander Sviridenko
#
BINDIR = .
CC=gcc
CFLAGS = $(COPTIONS) $(OPTFLAGS) $(INCLUDES)
LIBS = lm
LIBS = -lmetis -lm
LD = $(CC) $(LDOPTIONS) -L. -L..

all:
	g++ -lpython2.7 -lboost_python -I /usr/include/boost/ -I ./boost/graph/ \
	-I /usr/include/python2.7 -fpic -fPIC -shared \
	-o md.so md.cpp 

