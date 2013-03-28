#!/usr/bin/env python
#
# USAGE: python draw_interaction_graph.py PROBLEM_FILENAME

from __future__ import print_function

import gzip
import os
import sys
import networkx as nx
import pylab as plot

from les.readers.mps_reader import MPSReader
from les.interaction_graph import InteractionGraph

_EXT_READERS = {
  ".mps": MPSReader
}

def read_problem(filename):
  if not os.path.exists(filename):
    raise IOError("File doesn't exist: %s" % filename)
  root, ext = os.path.splitext(filename)
  if filename.endswith(".gz"):
    stream = gzip.open(filename, "rb")
    root, ext = os.path.splitext(root)
  else:
    stream = open(filename, "r")
  reader_class = _EXT_READERS.get(ext)
  if not reader_class:
    raise Exception("Doesn't know how to read %s format. See available formats."
                    % ext)
  reader = reader_class()
  reader.parse(stream)
  stream.close()
  return reader

def draw_interaction_graph(g):
  pos = nx.spring_layout(g)
  nx.draw_networkx_nodes(g, pos, node_color="white")
  nx.draw_networkx_edges(g, pos, edge_color="black", arrows=True)
  nx.draw_networkx_labels(g, pos, font_family="sans-serif")
  plot.axis("off")
  plot.show() # or plot.savefig("decomposition_tree.png")

def main():
  if len(sys.argv) < 2:
    print("USAGE: %s PROBLEM_FILENAME" % sys.argv[0], file=sys.stderr)
    print()
    print("Please provide input problem. "
          "Supported problem formats are: %s" % _EXT_READERS.keys(),
          file=sys.stderr)
    exit(0)
  try:
    reader = read_problem(sys.argv[1])
    draw_interaction_graph(InteractionGraph(reader.build_problem()))
  except KeyboardInterrupt, e:
    print("Interrupting...", file=sys.stderr)

if __name__ == "__main__":
  main()
