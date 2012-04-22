# Copyright (c) 2012 Alexander Sviridenko

# Target library directory and name
LES_LIBRARY_DIR = ../../lib
OSI_LESOLVER_LIBRARY_NAME = libosilesolver.so
LES_LIBRARY_PATH = $(LES_LIBRARY_DIR)/$(OSI_LESOLVER_LIBRARY_NAME)

OBJECTS = src/OsiLeSolverInterface.o

COINOR_DIR = /opt/SYMPHONY-5.4.0
COINOR_LIB = $(COINOR_DIR)/lib
COINOR_INCLUDE = -I$(COINOR_DIR)/include
INCLUDES = -DLES_DEBUG -I../../include $(COINOR_INCLUDE) -I./include

LIBS = -L$(COINOR_LIB) -L$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,$(COINOR_LIB) -lCoinUtils -lm -lOsi -lOsiSym -lSym -lOsiClp \
	-lCgl -lClp -lOsiClp -llapack -lblas -lles

%.o: %.cpp
	$(CXX) $(INCLUDES) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(LES_LIBRARY_PATH)

$(LES_LIBRARY_PATH): $(OBJECTS)
	$(CXX) -shared $(INCLUDES) $(LDFLAGS) -o $(LES_LIBRARY_PATH) $(OBJECTS) $(LIBS)

clean:
	rm $(OBJECTS) $(LES_LIBRARY_PATH)

