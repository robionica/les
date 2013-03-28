#!/usr/bin/env python
#
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

# USAGE: python draw_interaction_graph.py FILENAME

from __future__ import print_function

import os
import sys
import networkx as nx
import pylab as plot

from les.interaction_graph import InteractionGraph
from les.problems.bilp_problem import BILPProblem

def draw_interaction_graph(g):
  pos = nx.spring_layout(g)
  nx.draw_networkx_nodes(g, pos, node_color="white")
  nx.draw_networkx_edges(g, pos, edge_color="black", arrows=True)
  nx.draw_networkx_labels(g, pos, font_family="sans-serif")
  plot.axis("off")
  plot.show() # or plot.savefig("decomposition_tree.png")

def main():
  if len(sys.argv) < 2:
    print("USAGE: %s FILENAME" % sys.argv[0], file=sys.stderr)
    print()
    print("Please provide input problem.", file=sys.stderr)
    exit(0)
  try:
    draw_interaction_graph(InteractionGraph(BILPProblem.build(sys.argv[1])))
  except KeyboardInterrupt, e:
    print("Interrupting...", file=sys.stderr)

if __name__ == "__main__":
  main()
