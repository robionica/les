# Copyright (c) 2012 Oleksandr Sviridenko

include ../config.mk

INCLUDE_FLAGS = -I. $(LES_INCLUDE_FLAGS)
LIB_FLAGS = $(LES_LIB_FLAGS)

demo_finkelstein_decomposition:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_knapsack_problem_solver:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_interaction_graph:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_tree_decomposition:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

demo_celar_reader:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS)

# SYMPHONY

demo_pure_sym_solver:
	$(CXX) $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS) -lClp -lOsiClp -lCgl -lSym -lOsi -lOsiSym

demo_sym_solver_with_threads:
	g++ $@.cpp -o $@ $(SYMPHONY_INC) $(LIB) -lboost_thread -lboost_system

demo_symphony_with_lea:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

demo_relaxation:
	g++ $(SYMPHONY_INC) $(LIB) $@.cpp -o $@

simple_milp_problem:
	g++ $@.cpp -o $@ $(INCLUDE_FLAGS) $(LIB_FLAGS) -lsolver_symphony

clean:
	rm -f $(DEMOS)