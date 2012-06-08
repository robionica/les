#!/usr/bin/env python

__copyright__ = "Copyright (c) 2012 Alexander Sviridenko"

import sys

try:
    from networkx import Graph
except ImportError:
    print >>sys.stderr, "Please install networkx first:"
    print >>sys.stderr, "http://networkx.lanl.gov/"
    exit(1)

def minfill(G):
    """Min-fill heuristic method for elimination order. Return the
    number of fillins and eliminiation order."""
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
    H = eliminate_node(G, best_node)
    print ">>", H.edges(), ">", best_node
    fillins, order = minfill(H)
    return fillins + best_fills, (best_node,) + order

def eliminate_node(G, a):
    fillins = ()
    nb = frozenset(G.neighbors(a))
    for u in nb:
        for v in nb - frozenset((u,)):
            if not G.has_edge(v, u) and frozenset((u, v)) not in fillins:
                fillins += (frozenset((u, v)),)
    kill_edges = frozenset([(u, a) for u in nb] + [(a, u) for u in nb])
    H = Graph()
    H.add_nodes_from(list(frozenset(G.nodes()) - frozenset((a,))))
    H.add_edges_from(list((frozenset(G.edges()) - kill_edges) | frozenset(fillins)))
    return H
    
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
    print minfill(g)
