# Copyright (c) 2012 Alexander Sviridenko

# Target library directory and name
LES_LIBRARY_DIR = ../lib
LES_LIBRARY_NAME = libles.so
LES_LIBRARY_PATH = $(LES_LIBRARY_DIR)/$(LES_LIBRARY_NAME)

OBJECTS = decomposition/decomposer.o decomposition/tree_decomposition.o \
	decomposition/finkelstein.o graph.o interaction_graph.o milp_problem.o \
	quasiblock_milp_problem.o packed_vector.o packed_matrix.o utils/math.o \
	knapsack_problem.o

COINOR_DIR = /home/d2rk/lib/SYMPHONY
COINOR_LIB = $(COINOR_DIR)/lib
COINOR_INCLUDE = -I$(COINOR_DIR)/include
INCLUDES = -DLES_DEBUG -I.. $(COINOR_INCLUDE)

LIBS = -L$(COINOR_LIB) -Wl,--rpath -Wl,$(COINOR_LIB)

%.o: %.cpp
	$(CXX) -Wno-deprecated $(INCLUDES) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(LES_LIBRARY_PATH)

$(LES_LIBRARY_PATH): $(OBJECTS)
	$(CXX) -Wno-deprecated -shared $(INCLUDES) $(LDFLAGS) -o $(LES_LIBRARY_PATH) $(OBJECTS) $(LIBS)

clean:
	rm $(OBJECTS) $(LES_LIBRARY_PATH)
