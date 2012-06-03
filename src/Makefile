# Copyright (c) 2012 Alexander Sviridenko

# Target library directory and name
LES_LIBRARY_DIR = ../lib
LES_LIBRARY_NAME = libles.so
LES_LIBRARY_PATH = $(LES_LIBRARY_DIR)/$(LES_LIBRARY_NAME)

OBJECTS = decomposition/decomposer.o decomposition/tree_decomposition.o decomposition/finkelstein.o graph.o interaction_graph.o milp_problem.o \
	quasiblock_milp_problem.o packed_vector.o packed_matrix.o utils/math.o

COINOR_DIR = /opt/SYMPHONY-5.4.0
COINOR_LIB = $(COINOR_DIR)/lib
COINOR_INCLUDE = -I$(COINOR_DIR)/include
INCLUDES = -DLES_DEBUG -I../include $(COINOR_INCLUDE)

LIBS = -L$(COINOR_LIB) -Wl,--rpath -Wl,$(COINOR_LIB) -lCoinUtils -lm -lOsi -lOsiSym -lSym -lOsiClp \
	-lCgl -lClp -lOsiClp -llapack -lblas

%.o: %.cpp
	$(CXX) $(INCLUDES) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(LES_LIBRARY_PATH)

$(LES_LIBRARY_PATH): $(OBJECTS)
	$(CXX) -shared $(INCLUDES) $(LDFLAGS) -o $(LES_LIBRARY_PATH) $(OBJECTS) $(LIBS)

clean:
	rm $(OBJECTS) $(LES_LIBRARY_PATH)

