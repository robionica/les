# Copyright (c) 2012 Alexander Sviridenko

# Target library directory and name
LES_LIBRARY_DIR = ../../lib
OSI_LESOLVER_LIBRARY_NAME = libosilesolver.so
LES_LIBRARY_PATH = $(LES_LIBRARY_DIR)/$(OSI_LESOLVER_LIBRARY_NAME)

OBJECTS = src/OsiLeSolverInterface.o

COINOR_SYMPHONY_DIR = /home/d2rk/lib/SYMPHONY
COINOR_SYMPHONY_LIB = $(COINOR_SYMPHONY_DIR)/lib
COINOR_SYMPHONY_INCLUDE = -I$(COINOR_SYMPHONY_DIR)/include
INCLUDES = -DLES_DEBUG -I../../include $(COINOR_SYMPHONY_INCLUDE) -I./include

LIBS = -L$(COINOR_SYMPHONY_LIB) -L$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,$(LES_LIBRARY_DIR) -Wl,--rpath -Wl,$(COINOR_SYMPHONY_LIB) -lCoinUtils -lm -lOsi -lSym -lOsiClp \
	-lCgl -lClp -lOsiClp -llapack -lblas -lles # -lOsiSym

%.o: %.cpp
	$(CXX) $(INCLUDES) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(LES_LIBRARY_PATH)

$(LES_LIBRARY_PATH): $(OBJECTS)
	$(CXX) -shared $(INCLUDES) $(LDFLAGS) -o $(LES_LIBRARY_PATH) $(OBJECTS) $(LIBS)

clean:
	rm $(OBJECTS) $(LES_LIBRARY_PATH)

