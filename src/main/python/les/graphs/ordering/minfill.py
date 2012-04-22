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

import networkx
import sys

def _eliminate_node(G, a):
  fillins = ()
  nb = frozenset(G.neighbors(a))
  for u in nb:
    for v in nb - frozenset((u,)):
      if not G.has_edge(v, u) and frozenset((u, v)) not in fillins:
        fillins += (frozenset((u, v)),)
  kill_edges = frozenset([(u, a) for u in nb] + [(a, u) for u in nb])
  H = networkx.Graph()
  H.add_nodes_from(list(frozenset(G.nodes()) - frozenset((a,))))
  H.add_edges_from(list((frozenset(G.edges()) - kill_edges) | frozenset(fillins)))
  return H

def minfill(G):
  """Min-fill heuristic method for elimination order. Returns the number of
  fillins and eliminiation order.
  """
  best_node = None
  best_fills = None
  for node in G.nodes():
    fillins = ()
    nb = frozenset(G.neighbors(node))
    for u in nb:
      for v in nb - frozenset((u,)):
        if not G.has_edge(v, u) and frozenset((u, v)) not in fillins:
          fillins += (frozenset((u, v)),)
      if best_node == None or len(fillins) < best_fills:
        best_fills = len(fillins)
        best_node = node
  if best_node == None:
    return 0, tuple(G.nodes())
  H = _eliminate_node(G, best_node)
  fillins, order = minfill(H)
  return fillins + best_fills, (best_node,) + order
