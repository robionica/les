#!/usr/bin/env python

from __future__ import print_function

import gzip
import os
import sys
import networkx as nx
import pylab as plot

from les.readers.mps_reader import MPSReader
from les.interaction_graph import InteractionGraph

def main():
  if len(sys.argv) < 2:
    print("Please provide input MPS problem", file=sys.stderr)
    exit(0)
  reader = None
  filename = sys.argv[1]
  if not os.path.exists(filename):
    raise IOError("File doesn't exist: %s" % filename)
  if filename.endswith(".gz"):
    stream = gzip.open(filename, 'rb')
    reader = MPSReader()
    reader.parse(stream)
    stream.close()
  else:
    raise Exception()
  p = reader.build_problem()
  g = InteractionGraph(p)
  pos = nx.spring_layout(g)
  nx.draw_networkx_nodes(g, pos, node_color="white")
  nx.draw_networkx_edges(g, pos, edge_color="black", arrows=True)
  nx.draw_networkx_labels(g, pos, font_family="sans-serif")
  plot.axis("off")
  plot.show() # or plot.savefig("decomposition_tree.png")

if __name__ == "__main__":
  main()
