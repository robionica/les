# Copyright (c) 2012-2013 Oleksandr Sviridenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import networkx as nx
import pylab as plot
import numpy as np
import sys
import os
import gzip

from les.problems import BILPProblem
from les.decomposers import FinkelsteinQBDecomposer
from les.readers.mps_reader import MPSReader

def draw_decomposition_tree(g):
  """Draws decomposition tree g."""
  pos = nx.spring_layout(g)
  nx.draw_networkx_nodes(g, pos, node_color="white")
  nx.draw_networkx_edges(g, pos, edge_color="black", arrows=True)
  nx.draw_networkx_labels(g, pos, font_family="sans-serif")
  edge_labels = dict([((u,v), list(d["shared_cols"]))
                      for u, v, d in g.edges(data=True)])
  nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
  plot.axis("off")
  plot.show() # or plot.savefig("decomposition_tree.png")

def main():
  if len(sys.argv) < 2:
    print("Please provide input problem", file=sys.stderr)
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
  problem = reader.build_problem()
  decomposer = FinkelsteinQBDecomposer()
  decomposer.decompose(problem)
  draw_decomposition_tree(decomposer.get_decomposition_tree())

if __name__ == "__main__":
  main()
