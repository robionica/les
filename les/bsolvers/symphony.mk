# Copyright (c) 2012 Alexander Sviridenko

include ../../tmp.mk

# Target library directory and name
BSOLVER_LIB_FILE_NAME = libbsolver_symphony.so
BSOLVER_LIB_FILE_PATH = $(LES_LIB_DIR_PATH)/$(BSOLVER_LIB_FILE_NAME)

OBJECTS = symphony.o

%.o: %.cpp
	$(CXX) $(LES_INCLUDE_FLAGS) -lboost_filesystem -lboost_program_options -lboost_graph -fPIC -g -c $< -o $@

all: $(BSOLVER_LIB_FILE_PATH)

$(BSOLVER_LIB_FILE_PATH): $(OBJECTS)
	$(CXX) -shared $(LES_INCLUDE_FLAGS) $(LDFLAGS) -o $(LES_LIB_FILE_PATH) $(OBJECTS) $(LES_LIB_FLAGS)

clean:
	rm $(OBJECTS) $(BSOLVER_LIB_FILE_PATH)
