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

import networkx as nx
import pylab as plot
import numpy as np

from les.problems import MILPProblem
from les.decomposers import FinkelsteinQBDecomposer

# Build the problem
cons_matrix = np.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                         [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                         [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                         [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                         [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                         [0., 0., 0., 0., 0., 0., 3., 4., 1.]])
problem = MILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                      cons_matrix,
                      None,
                      [7, 6, 9, 7, 3, 5])
# Decompose the problem
decomposer = FinkelsteinQBDecomposer()
decomposer.decompose(problem)
# Draw decomposition tree
g = decomposer.get_decomposition_tree()
pos = nx.spring_layout(g)
nx.draw_networkx_nodes(g, pos, node_color="white")
nx.draw_networkx_edges(g, pos, edge_color="black", arrows=True)
nx.draw_networkx_labels(g, pos, font_family="sans-serif")
edge_labels = dict([((u,v), list(d["shared_cols"]))
                    for u, v, d in g.edges(data=True)])
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
plot.axis("off")
plot.show() # or plot.savefig("decomposition_tree.png")
