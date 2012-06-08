
from networkx import Graph
from md import md_ordering

def minimum_degree_ordering(g):
    xadj = [0]
    adjncy = []
    adjacency = g.adjacency_list()
    for i in range(len(adjacency)):
        adj = adjacency[i]
        if adj:
            assert max(adj) < len(adjacency)
        adjncy += map(int, adj)
        xadj.append(len(adjncy))
    return list(md_ordering(xadj, adjncy))

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
    print minimum_degree_ordering(g)   

