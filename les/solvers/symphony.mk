# Copyright (c) 2012 Oleksandr Sviridenko

include ../../config.mk

SYMPHONY_LIB_FILE_NAME = libles_symphony_wrapper.so
SYMPHONY_LIB_FILE_PATH = $(LES_LIB_DIR_PATH)/$(SYMPHONY_LIB_FILE_NAME)

INCLUDE_FLAGS = $(LES_INCLUDE_FLAGS) $(COINOR_INCLUDE_FLAGS)
LIB_FLAGS = $(COINOR_LIB_FLAGS) $(LES_LIB_FLAGS) \
	-lboost_filesystem -lboost_program_options -lboost_graph

OBJECTS = symphony_wrapper.o

%.o: %.cpp
	$(CXX) $(INCLUDE_FLAGS) $(LIB_FLAGS) -fPIC -g -c $< -o $@

all: $(SYMPHONY_LIB_FILE_PATH)

$(SYMPHONY_LIB_FILE_PATH): $(OBJECTS)
	$(CXX) -shared $(INCLUDE_FLAGS) $(LDFLAGS) -o $(SYMPHONY_LIB_FILE_PATH) $(OBJECTS) $(LIB_FLAGS)

clean:
	rm $(OBJECTS) $(SYMPHONY_LIB_FILE_PATH)
