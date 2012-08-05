# Copyright (c) 2012 Alexander Sviridenko

include ../config.mk

OBJECTS = decomposition/decomposer.o decomposition/tree_decomposition.o \
	decomposition/finkelstein.o graph.o interaction_graph.o milp_problem.o \
	quasiblock_milp_problem.o packed_vector.o packed_matrix.o utils/math.o \
	knapsack_problem.o

%.o: %.cpp
	$(CXX) -Wno-deprecated $(LES_INCLUDE_FLAGS) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(LES_LIB_FILE_PATH)

$(LES_LIB_FILE_PATH): $(OBJECTS)
	$(CXX) -Wno-deprecated -shared $(INCLUDES) $(LDFLAGS) -o $(LES_LIB_FILE_PATH) $(OBJECTS) $(LIBS)

clean:
	rm $(OBJECTS) $(LES_LIB_FILE_PATH)
