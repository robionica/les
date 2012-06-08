#!/usr/bin/env python

"""http://en.wikipedia.org/wiki/Lexicographic_breadth-first_search"""

__copyright__ = "Copyright (c) 2012 Alexander Sviridenko"

import sys

try:
    from networkx import Graph
except ImportError:
    print >>sys.stderr, "Please, install networkx first"
    exit(1)

def arbitrary_item(S):
    """Select an arbitrary item from set or sequence S.
    Avoids bugs caused by directly calling iter(S).next() and
    mysteriously terminating loops in callers' code when S is empty."""
    try:
        return iter(S).next()
    except StopIteration:
        raise IndexError("No items to select.")

def lex_bfs_ordering(g):
    """Return the graph vertices ordered by lexicographic breadth-first
    search.
    
    The algorithm is implement as described in :

    Habib, Michel; McConnell, Ross; Paul, Christophe; Viennot, Laurent (2000),
    "Lex-BFS and partition refinement, with applications to transitive
    orientation, interval graph recognition and consecutive ones testing",
    Theoretical Computer Science 234 (1--2): 59--84, doi:10.1016/S0304-3975(97)00241-7.
    See http://www.cs.colostate.edu/~rmm/lexbfs.ps"""
    # initialize a sequence S of sets, to contain a single set containing
    # all vertices
    S = [set(g.nodes().reverse())]
    # while sequence of sets is non-empty
    while len(S):
        # find and remove a vertex v from the first set in S
        s = S[0]
        v = arbitrary_item(s)
        print S, v
        # if the first set in S is now empty, remove it from S
        s.remove(v)
        # add v to the end of the output sequence
        yield v
        n = set(g.neighbors(v))
        new_S = []
        for s in S:
            D = s & n
            if D:
                new_S.append(D)
            D = s - n
            if D:
                new_S.append(D)
        S = new_S

def lex_bfs(g):

    l = []
    f = []
    order = []
    n = len(g.nodes())
    for u in g.nodes():
        l.append([])
        f.append(-1)
        order.append(-1)
    for i in range(n-1, -1, -1):
        # search for the vertex u with a greatest label in the lexicographic
        u = 0
        for j in range(n):
            if f[j] == -1 and len(l[j]) > len(l[u]):
                u = j
        print l
        f[u] = i
        order[i] = u
        for v in g.adjacency_list()[u]:
            if f[v] == -1:
                l[v].append(i)
    return order

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
    print list(lex_bfs_ordering(g))

