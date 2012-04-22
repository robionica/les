#
# Copyright (c) 2012 Alexander Sviridenko
#

ROOT = ..
INCLUDES = -I$(ROOT)/include -I/opt/SYMPHONY-5.4.0/include -I./include
LES_LIBRARY_DIR = ../lib/

SYMPHONY_LIBS = -lz -lbz2  -Wl,--rpath -Wl,/opt/SYMPHONY-5.4.0/lib
LIB = -L$(LES_LIBRARY_DIR) $(SYMPHONY_LIBS) -lles -Wl,--rpath -Wl,$(LES_LIBRARY_DIR)

demo_finkelstein_decomposition:
	g++ $(INCLUDES) $(LIB) src/demo_qbmilpp.cpp src/demo_finkelstein_decomposition.cpp -o $@


