#
# Copyright (c) 2012 Alexander Sviridenko
#

ROOT = ..
INCLUDES = -I$(ROOT)/include -I/opt/SYMPHONY-5.4.0/include -I./include
LES_LIBRARY_DIR = ../lib/

SYMPHONY_HOME_DIR = /home/d2rk/lib/SYMPHONY
SIMPHONY_INC = -I$(ROOT)/include -I/opt/SYMPHONY-5.4.0/include -I../include
SYMPHONY_LIB = -L$(LES_LIBRARY_DIR) -lz -lbz2 -losilesolver -Wl,--rpath -Wl,$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,$(SYMPHONY_HOME_DIR)/lib
LIB = -L$(LES_LIBRARY_DIR) $(SYMPHONY_LIB) -lles -Wl,--rpath -Wl,$(LES_LIBRARY_DIR)

DEMOS = demo_finkelstein_decomposition demo_interaction_graph	\
	demo_tree_decomposition demo_celar_reader

demo_finkelstein_decomposition:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB)

demo_knapsack_problem:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB)

demo_interaction_graph:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB)

demo_tree_decomposition:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB)

demo_celar_reader:
	g++ $@.cpp -o $@ $(INCLUDES) $(LIB)

# SYMPHONY

demo_threads:
	g++ $@.cpp -o $@ $(SYMPHONY_INC) $(LIB) -lboost_thread -lboost_system

demo_symphony_with_lea:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

demo_relaxation:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

simple_milp_problem:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

clean:
	rm -f $(DEMOS)