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
import pylab

from les import decomposers
from les import mp_model
from les.graphs import decomposition_tree
from les.utils import logging
from les.cli.commands import command_base

DEFAULT_DECOMPOSER_ID = decomposers.FINKELSTEIN_QB_DECOMPOSER_ID
DEFAULT_NODE_COLOR = 'white'

class DrawDecompositionTree(command_base.CommandBase):

  def run(self):
    model = mp_model.build(self._args.file)
    decomposer = decomposers.get_instance_of(self._args.decomposer_id, model)
    try:
      decomposer.decompose()
    except Exception, e:
      logging.exception('Cannot decompose the model.')
      return
    g = decomposer.get_decomposition_tree()
    pos = networkx.spring_layout(g)
    networkx.draw_networkx_nodes(g, pos, node_color=self._args.node_color)
    networkx.draw_networkx_edges(g, pos, edge_color='black', arrows=True)
    networkx.draw_networkx_labels(g, pos, font_family='sans-serif')
    edge_labels = dict([((u,v), list(d['shared_variables'])) for u, v, d in
      g.edges(data=True)])
    networkx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
    pylab.axis('off')
    pylab.show() # or plot.savefig("decomposition_tree.png")

  @classmethod
  def setup_argparser(self, argparser):
    argparser.add_argument('--decomposer', dest='decomposer_id', type=int,
                           metavar='ID', default=DEFAULT_DECOMPOSER_ID,
                           help=('decomposer id (default: %d)'
                           % DEFAULT_DECOMPOSER_ID))
    argparser.add_argument('--node-color', dest='node_color', type=str,
                           metavar='STR', default=DEFAULT_NODE_COLOR,
                           help=('node color (default: %s)'
                           % DEFAULT_NODE_COLOR))
