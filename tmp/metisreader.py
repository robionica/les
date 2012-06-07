"""MetisReader reads the METIS graph format"""

import re

import networkx

def _make_networkx_graph(reader):
    g = networkx.Graph()
    for (vertice, neighbors) in reader.get_adjacency().iteritems():
        for neighbor in neighbors:
            g.add_edge(vertice, neighbor)
    reader.set_graph(g)

_supported_graph_handlers = {
    'networkx': _make_networkx_graph
}

def _read_metis_format(reader):
    num_vertices = 0
    num_edges = 0
    adjacency = {}
    current_vertice = 0
    for line in reader.get_input():
        # Skip comments and empty lines
        if re.match("^\s*\%", line) or re.match("^\s*$", line):
            continue
        if not num_vertices or not num_edges:
            # The first line containts either two (n, m), three (n, m, fmt), 
            # or four (f, m, fmt, ncon) integers
            info = re.match("^\s*(\d+)\s*(\d+)\s*(\d+)?\s*(\d+)?\s*", line)
            assert info, "Format can not be read"
            num_vertices = int(info.group(1))
            num_edges = int(info.group(2))
            for vertice in range(num_vertices):
                adjacency[vertice] = []
            continue
        re.sub("\s+", " ", line)
        neighbors = [int(_)-1 for _ in line.split()]
        adjacency[current_vertice] = neighbors
        current_vertice += 1
    reader.set_adjacency(adjacency)
    reader.set_number_vertices(num_vertices)
    reader.set_number_edges(num_edges)

def _read_csp_format(reader):
    """http://www.dbai.tuwien.ac.at/proj/hypertree/downloads.html"""
    num_vertices = 0
    num_edges = 0
    adjacency = {}
    buf = []

    names = {}
    next_id = 0
    rels = []
    maxn = 0
    maxrel = 0
    for line in reader.get_input():
        # Skip comments
        if re.match("^\s*\%", line):
            continue
        info = re.match("^\s*[a-zA-Z\_\:0-9]+\d+\s*\((.*?)\)", line)
        if info:
            block = []
            for item in info.group(1).split(','):
                item = item.strip()
                if not names.has_key(item):
                    names[item] = next_id
                    next_id = next_id + 1
                n = names[item]
                if n > maxn: maxn = n
                block.append(n)
            rels.append(block)
            maxrel += (len(block) * (len(block) - 1)) / 2

    num_vertices = next_id
    num_edges = maxrel

    for i in range(num_vertices):
        adjacency[i] = []

    for rel in rels:
        for i in range(len(rel)):
            for j in range(len(rel)):
                if i == j: continue
                adjacency[rel[i]].append(rel[j])

    reader.set_adjacency(adjacency)
    reader.set_number_vertices(num_vertices)
    reader.set_number_edges(num_edges)
# _read_csp_format

_supported_format_handlers = {
    'metis': _read_metis_format,
    'csp': _read_csp_format
}

#_______________________________________________________________________________

class MetisReader:
    def __init__(self, file_path, input_format='metis', graph_handler='networkx'):
        self._input = []
        self._num_vertices = 0
        self._num_edges = 0
        self._adjacency = {} # adjacency table
        self._xadj = [0]
        self._adjncy = []
        # File path is presented
        self._file_path = file_path
        if self._file_path:
            try:
                f = open(self._file_path, "r")
            except IOError:
                print "There were problems reading '%s'\n" % self._file_path
                traceback.print_exc(file=sys.stderr)
                raise
            self._input = f.readlines()
            f.close()
        # Read the input format
        self._input_format = input_format.lower()
        assert _supported_format_handlers.has_key(self._input_format), \
            "MetisReader can not read '%s' format" % self._input_format
        # Prepare the graph
        self._graph = None
        self._graph_handler = graph_handler.lower()
        assert _supported_graph_handlers.has_key(self._graph_handler), \
            "MetisReader doesnot have '%s' handler" % self._input_format
        self.read()

    def read(self):
        _supported_format_handlers[self._input_format](self)

        self._xadj = [0]
        self._adjncy = []
        for i in range(len(self._adjacency)):
            adj = self._adjacency[i]
            assert max(adj) < len(self._adjacency), "!"
            self._adjncy += adj
            self._xadj.append(len(self._adjncy))
    # read()

    def save_as(self, file_path):
        f = open(file_path, "w")
        f.write("%d %d\n" % (self._num_vertices, self._num_edges))
        for v in sorted(self._adjacency.keys()):
            f.write(" ".join([str(nb + 1) for nb in self._adjacency[v]]) + "\n")
        f.close()

    def get_number_vertices(self):
        return self._num_vertices

    def set_number_vertices(self, num_vertices):
        self._num_vertices = num_vertices

    def set_number_edges(self, num_edges):
        self._num_edges = num_edges

    def get_number_edges(self):
        return self._num_edges

    def get_input(self):
        return self._input

    def get_input_format(self):
        return self._input_format

    def get_graph_handler(self):
        return self._graph_handler

    def set_adjacency(self, adjacency):
        self._adjacency = adjacency

    def get_adjacency(self):
        return self._adjacency

    def get_xadj(self):
        return self._xadj

    def get_graph(self):
        if not self._graph:
            _supported_graph_handlers[self._graph_handler](self)
        return self._graph

    def set_graph(self, graph):
        self._graph = graph
