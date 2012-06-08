#!/usr/bin/env python

__copyright__ = "Copyright (c) 2012 Alexander Sviridenko"

import sys
from networkx import Graph
try:
    import pymetis._internal as pymetis
except:
    print >>sys.stderr, "Please, install pymetis first:"
    print >>sys.stderr, "http://pypi.python.org/pypi/PyMetis"
    exit(1)

def nd_ordering(g):
    xadj = [0]
    adjncy = []
    adjacency = g.adjacency_list()

    for i in range(len(adjacency)):
        adj = adjacency[i]
        if adj:
            assert max(adj) < len(adjacency)
        adjncy += map(int, adj)
        xadj.append(len(adjncy))
    (perm, iperm) = pymetis.edge_nd(xadj, adjncy)
    return perm

if __name__ == "__main__":
    g = Graph()
    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_node(6)
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 0)
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(1, 4)
    g.add_edge(2, 0)
    g.add_edge(2, 1)
    g.add_edge(2, 3)
    g.add_edge(2, 5)
    g.add_edge(2, 6)
    g.add_edge(5, 6)
    print nd_ordering(g)
