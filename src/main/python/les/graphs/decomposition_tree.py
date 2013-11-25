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

'''Decomposition tree contains a set of independent models created from
original model of the given problem with help of decomposers.
'''

import networkx as nx

from les import mp_model
from les.utils import logging

class Node(dict):
  '''Name of the node equals to the name of the models it holds.'''

  def __init__(self, model):
    dict.__init__(self)
    self['model'] = model
    self['shared_variables'] = set()
    self['local_variables'] = set()

  def __hash__(self):
    return hash(self.get_name())

  def __str__(self):
    return ('%s[name="%s", num_shared_vars=%d, num_local_vars=%d]' %
            (self.__class__.__name__, self.get_name(),
             self.get_num_shared_variables(), len(self['local_variables'])))

  def get_name(self):
    return self['model'].get_name()

  def get_model(self):
    return self['model']

  def get_local_variables(self):
    return self['local_variables']

  def get_num_shared_variables(self):
    return len(self['shared_variables'])

  def get_shared_variables(self):
    return self['shared_variables']

class Edge(dict):

  def __init__(self, source, dest, shared_variables=[]):
    dict.__init__(self)
    self['source'] = source
    self['dest'] = dest
    if not type(shared_variables) in (list, set):
      raise TypeError('shared_variables must be a sequence: %s'
                      % type(shared_variables))
    if not all([type(name) is unicode for name in shared_variables]):
      raise TypeError('shared_variables has to be a list of unicode strings: '
                      + str(shared_variables))
    self['shared_variables'] = set(shared_variables)

  def __str__(self):
    return '%s[source="%s", dest="%s", num_shared_vars=%d]' \
        % (self.__class__.__name__, self['source'].get_name(),
           self['dest'].get_name(), self.get_num_shared_variables())

  def get_dest(self):
    return self['dest']

  def get_num_shared_variables(self):
    return len(self['shared_variables'])

  def get_shared_variables(self):
    return self['shared_variables']

  def get_source(self):
    return self['source']

class DecompositionTree(nx.DiGraph):
  '''This class represents decomposition tree.

  :param model: A :class:`~les.model.Model` derived
    instance.
  :param root: A root node.
  '''

  Edge = Edge

  def __init__(self, model, root=None):
    nx.DiGraph.__init__(self)
    if not isinstance(model, mp_model.MPModel):
      raise TypeError('model must be derived from MPModel')
    self._model = model
    if not root is None:
      self.set_root(root)

  def __str__(self):
    return ('%s[num_nodes=%d, num_edges=%d]',
            (self.__class__.__name__, self.get_num_nodes(),
             self.get_num_edges()))

  def add_node(self, node_or_model):
    '''Adds new node to the tree where the node is represented by a model.

    :param node_or_model: A :class:`~ModelParameters` derived instance or
      :class:`Node` instance.
    :raises: :exc:`TypeError`
    '''
    node = node_or_model
    if not isinstance(node, Node):
      if not isinstance(node_or_model, mp_model.MPModel):
        raise TypeError('node_or_model must be derived from '
                        'MPModel: %s' % node)
      node = Node(node_or_model)
    model = node.get_model()
    # Generate model name if necessary.
    if model.get_name() is model.default_model_name:
      model.set_name('%s_%s' % (self._model.get_name(),
                                model.model_name_format % len(self)))
    super(DecompositionTree, self).add_node(model.get_name(), node)
    return node

  def add_nodes(self, nodes):
    for node in nodes:
      self.add_node(node)

  def copy(self):
    '''Returns graph shallow copy.

    :returns: A :class:`DecompositionTree` instance.
    '''
    tree = DecompositionTree(self._model, self._root)
    tree.add_nodes_from(self.nodes(data=True))
    tree.add_edges_from(self.edges(data=True))
    return tree

  def get_num_nodes(self):
    '''Returns number of nodes in the tree.'''
    return len(self.get_nodes())

  def get_nodes(self):
    return [self.node[_] for _ in nx.DiGraph.nodes(self)]

  def get_num_edges(self):
    '''Returns number of edges in the tree.'''
    return len(self.get_edges())

  def get_root(self):
    '''Returns root node.'''
    return self._root.get_name()

  def merge_nodes(self, node1, node2):
    '''Merges `node1` and `node2` to `node1` and removes `node2`. Creates new
    model.
    '''
    model = self.node[node1]['model'] + self.node[node2]['model']
    self.add_node(model)
    for edge in self.edges(node2, data=True):
      self.add_edge(model, self.node[edge[1]]['model'],
                    edge[2].get('shared_cols'))
    self.remove_node(node2)
    self.remove_node(node1)
    # Did we remove the root?
    if self.get_root() in (node1, node2):
      self._root = model

  def is_leaf(self, u):
    '''Defines whether or not the given node is a leave.

    :returns: `True` or `False`.
    '''
    return self.out_degree(u) == 0

  def get_leaves(self):
    '''Returns a list of leaves of this tree.'''
    return filter(self.is_leaf, self.nodes())

  def remove_node(self, node):
    for other in self.predecessors(node):
      self.node[node]['model'].remove_dependecy(self.node[other]['model'])
    for other in self.successors(node):
      self.node[other]['model'].remove_dependecy(self.node[node]['model'])
    super(DecompositionTree, self).remove_node(node)

  def get_edge_between(self, node1, node2):
    return Edge(**self.edge[node1][node2])

  def add_edge(self, *args, **kwargs):
    '''Adds an edge between `source` and `dest`. `shared_variables` represents a
    list of variables, how `source` depends on `dest`. Returns edge object.

    :param shared_variables: A list of variables.
    :return: An :class:`Edge` instance.
    '''
    edge = None
    if len(args) == 1:
      edge = args[0]
      if not isinstance(edge, Edge):
        raise TypeError()
    else:
      edge = Edge(*args, **kwargs)
    nx.DiGraph.add_edge(self, edge.get_source().get_name(),
                        edge.get_dest().get_name(),
                        edge)
    logging.debug("Add edge between %s and %s with %d shared variable(s)",
                  edge.get_source().get_name(), edge.get_dest().get_name(),
                  edge.get_num_shared_variables())
    for node in (self.node[edge.get_source().get_name()],
                 self.node[edge.get_dest().get_name()]):
      node['shared_variables'] |= edge.get_shared_variables()
      node['local_variables'] = (
        set([var.get_name() for var in node['model'].get_variables()])
        - set(node['shared_variables']))
    return edge

  def get_models(self):
    '''Returns a list of all models parameters from the tree.

    :returns: A list of :class:`~Model` instances.
    '''
    return [self.node[n]['model'] for n in self.nodes()]

  def set_root(self, root):
    self._root = root

DecompositionTree.get_edges = DecompositionTree.edges
