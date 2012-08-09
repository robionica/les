# Copyright (c) 2012 Alexander Sviridenko

include ../config.mk

INCLUDE_FLAGS = -I. $(LES_INCLUDE_FLAGS)
LIB_FLAGS = $(LES_LIB_FLAGS)

DEMOS = demo_finkelstein_decomposition \
	demo_interaction_graph \
	demo_tree_decomposition \
	demo_celar_reader

demo_finkelstein_decomposition:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_knapsack_problem:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_interaction_graph:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_tree_decomposition:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_celar_reader:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

# SYMPHONY

demo_symphony:
	$(CXX) $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS) -lClp -lOsiClp -lCgl -lSym -lOsi -lOsiSym -lsolver_symphony

demo_threads:
	g++ $@.cpp -o $@ $(SYMPHONY_INC) $(LIB) -lboost_thread -lboost_system

demo_symphony_with_lea:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

demo_relaxation:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

simple_milp_problem:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS) -lsolver_symphony

clean:
	rm -f $(DEMOS)