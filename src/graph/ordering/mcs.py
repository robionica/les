
import sys
from networkx import Graph  
from cvxopt import matrix, spmatrix, printing

try:
    import chompack
except ImportError:
    print >>sys.stderr, "Please, install chompack."
    print >>sys.stderr, "Use can install SMCP: http://abel.ee.ucla.edu/smcp/download/index.html"
    sys.exit(1)

def get_mcs_ordering(G):
    V = []
    I = []
    J = []
    for node in G.nodes():
        for neighbor in G.neighbors(node) + [node]:
            V.append(1.0)
            J.append(node)
            I.append(neighbor)
    A = spmatrix(V, I, J)
    return list(chompack.maxcardsearch(A))
    
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
    print get_mcs_ordering(g)
