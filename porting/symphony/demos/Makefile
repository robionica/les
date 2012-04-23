# Copyright (c) 2012 Alexander Sviridenko

ROOT = ../../..
SRC = $(ROOT)/src
INCLUDES = -I$(ROOT)/include -I/opt/SYMPHONY-5.4.0/include -I../include
LES_LIBRARY_DIR = $(ROOT)/lib/

LIB = -L$(LES_LIBRARY_DIR) -lz -lbz2 -lles -losilesolver -Wl,--rpath -Wl,$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,/opt/SYMPHONY-5.4.0/lib

demo_threads:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB) -lboost_thread -lboost_system

demo_symphony_with_lea:
	g++ $(INCLUDES) $(LIB) $@.cpp -o $@

simple_milp_problem:
	g++ $(INCLUDES) $(LIB) $@.cpp -o $@

all: demo_threads demo_symphony_with_lea simple_milp_problem