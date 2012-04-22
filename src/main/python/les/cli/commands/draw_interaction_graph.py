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

from les import mp_model
from les.graphs import interaction_graph
from les.cli.commands import command_base
from les.utils import logging

DEFAULT_NODE_COLOR = 'white'

class DrawInteractionGraph(command_base.CommandBase):

  @classmethod
  def setup_argparser(self, argparser):
    argparser.add_argument('--node-color', dest='node_color', type=str,
                           metavar='STR', default=DEFAULT_NODE_COLOR,
                           help=('node color (default: %s)'
                           % DEFAULT_NODE_COLOR))

  def run(self):
    try:
      model = mp_model.build(self._args.file)
    except Exception, e:
      logging.exception('Cannot read the model.')
      return
    g = interaction_graph.InteractionGraph(model)
    pos = networkx.spring_layout(g)
    networkx.draw_networkx_nodes(g, pos, node_color=self._args.node_color)
    networkx.draw_networkx_edges(g, pos, edge_color='black', arrows=True)
    networkx.draw_networkx_labels(g, pos, font_family='sans-serif')
    pylab.axis('off')
    # TODO: allow user to save the result figure, e.g. plot.savefig(<FILENAME>).
    pylab.show()
