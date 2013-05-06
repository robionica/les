# -*- coding: utf-8; -*-
#
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

""":class:`LocalEliminationSolver` represents the general class of local
elimination algorithms (LEA) for computing information, that have decomposition
approach and that allow to calculate some global information about a solution of
the entire problem using local computations.
"""

import time
import networkx as nx
import logging

from les.problems.bilp_problem import BILPProblem
from les.decomposition_tree import DecompositionTree
from les.solvers.bilp_solver_base import BILPSolverBase
from les.solvers.local_elimination_solver.data_models.data_model import DataModel
from les.solvers.local_elimination_solver.data_models.sqlite_data_model import SQLiteDataModel
from les.solvers.local_elimination_solver.parallelizers import \
    ThreadParallelizerFactory, ParallelizerFactory
from les.solvers.local_elimination_solver import local_solver
from les.solvers.solver_factory import SolverFactory

class Error(Exception):
  """Base-class for exceptions in this module."""

class Params(object):
  """This class represents :class:`LocalEliminationSolver` parameters."""

  def __init__(self):
    self._data_model_type = SQLiteDataModel
    self._master_solver_factory = None
    self._parallelizer_factory = None
    self._relaxation_solver_factories = []

  @property
  def relaxation_solver_factories(self):
    return self._relaxation_solver_factories

  @relaxation_solver_factories.setter
  def relaxation_solver_factories(self, factories):
    if not isinstance(factories, (list, tuple)):
      raise TypeError()
    for factory in factories:
      if not isinstance(factory, SolverFactory):
        raise TypeError()
    self._relaxation_solver_factories = factories

  @property
  def parallelizer_factory(self):
    return self._parallelizer_factory

  @parallelizer_factory.setter
  def parallelizer_factory(self, factory):
    if not isinstance(factory, ParallelizerFactory):
      raise TypeError("factory must be derived from ParallelizerFactory")
    self._parallelizer_factory = factory

  @property
  def master_solver_factory(self):
    return self._master_solver_factory

  @master_solver_factory.setter
  def master_solver_factory(self, solver_factory):
    if not isinstance(solver_factory, SolverFactory):
      raise TypeError("solver_factory must be derived from SolverFactory: %s"
                      % solver_factory)
    self._master_solver_factory = solver_factory

  @property
  def data_model_type(self):
    return self._data_model_type

  @data_model_type.setter
  def data_model_type(self, data_model_type):
    """Set :class:`DataModel` class to use.

    Returns:
      :class:`DataModel` subclass.
    """
    if not issubclass(data_model_type, DataModel):
      raise TypeError()
    self._data_model_type = data_model

class LocalEliminationSolver(BILPSolverBase):
  """This class represents local elimination solver (LES), which implements
  local elimination algorithm (LEA). The solver solves discrete optimization
  problems (DOP) defined by :class:`BILPProblem` class.

  :param master_solver_factory: A :class:`SolverFactory` to use as master solver
       factory.
  :param relaxation_solver_factories: A list of :class:`SolverFactory` instances
       that will be used as relaxation solver factories.
  :param parallelizer_factory: :class:`Parallelizer` instance that provides
       parallel support. By default :class:`ThreadParallelizerFactory` will be
       used.
  :param data_model: A :class:`DataModel` instance that will help solver to keep
       local solutions.
  """

  Params = Params

  # Logger for this class
  logger = logging.getLogger()

  DEFAULT_PARALLELIZER_FACTORY_CLASS = ThreadParallelizerFactory

  def __init__(self, master_solver_factory=None, data_model=None,
               parallelizer_factory=None):
    BILPSolverBase.__init__(self)
    self._obj_value = 0.0
    self._col_solution = []
    self._decomposition_tree = None
    self._params = Params()
    self._data_model = None
    if data_model:
      self.set_data_model(data_model)
    if master_solver_factory:
      self._params.master_solver_factory = master_solver_factory
    self._params.parallelizer_factory = parallelizer_factory \
        or self.DEFAULT_PARALLELIZER_FACTORY_CLASS()

  def set_data_model(self, data_model):
    if not isinstance(data_model, DataModel):
      raise TypeError()
    self._params.data_model_type = type(data_model)

  def get_data_model(self):
    """Returns data model.

    :returns: A :class:`DataModel` derived instance.
    """
    return self._data_model

  @property
  def params(self):
    return self._params

  def set_params(self, **kwargs):
    for key, value in kwargs.items():
      if not hasattr(self._params, key):
        raise Exception()
      self._params.__setattr__(key, value)

  def get_col_solution(self):
    """Returns a list of primal variable values.

    :returns: A list of variable values.
    """
    return self._col_solution

  def get_problem(self):
    """Returns problem that has to be solved by this solver.

    :returns: A :class:`~les.problems.bilp_problem.BILPProblem` based problem
      instance.
    """
    return self._problem

  def solve(self):
    """Starts solving of an active problem model.

    .. note::

       If we have only one subproblem which is the actual problem, it will be
       solved with pure master solver.

    :rises: :class:`Error`
    """
    if not self.get_problem():
      raise Error("Nothing to be solved, problem model is empty.")
    self._col_solution = [0.0] * self._problem.get_num_variables()
    if not self.get_data_model():
      cls = self.params.data_model_type
      self._data_model = cls()
    self._parallelizer = self.params.parallelizer_factory.build()
    local_solver_factory = self._parallelizer.get_local_solver_factory()
    local_solver_factory.set_data_model(self._data_model)
    local_solver_factory.set_params(self.params)

    subproblems = self._decomposition_tree.get_subproblems()

    self.logger.info("Solving problem %s" % self._problem.get_name())
    if len(subproblems) == 1:
      solver = self._params.master_solver_factory.build()
      solver.load_problem(self._problem)
      solver.solve()
      self._obj_value = solver.get_obj_value()
      self._col_solution = solver.get_col_solution()
    else:
      self.logger.debug("Estimated number of problems to be solved: %d"
         % sum([1 << problem.get_num_shared_variables() for problem in subproblems]))
      start = time.clock()
      self._data_model.configure(subproblems)
      end = time.clock()
      self.logger.debug("Configure data model time = %6.4f sec(s)" % (end - start,))
      # Setup and run parallelizer
      map(self._parallelizer.put, subproblems)
      #self._parallelizer.put(subproblems[0])
      self._parallelizer.run()
      start = time.clock()
      self._process_local_solutions()
      end = time.clock()
      self.logger.debug("Process local solution time = %6.4f sec(s)" % (end - start,))

  def _process_local_solutions(self):
    """Process subproblems in a depth-first-search pre-ordering starting from
    the root.
    """
    self.logger.info("Processing local solutions...")
    for node in nx.dfs_preorder_nodes(self._decomposition_tree,
                                      self._decomposition_tree.get_root()):
      subproblem = self._decomposition_tree.node[node]["subproblem"]
      self._data_model.process(subproblem)
    self._obj_value, signed_cols = self._data_model.get_solution(subproblem.get_name())
    try:
      map(lambda signed_col: self._col_solution.__setitem__(int(signed_col), 1.0),
          signed_cols.split(','))
    except ValueError, e:
      print ">%s<" % signed_cols
      print e
      exit(0)

  def load_problem(self, problem, decomposition_tree, max_num_shared_cols=10):
    """Loads problem and its decomposition model represented by decomposition
    tree. Process `decomposition_tree` and merge nodes according to
    `max_num_shared_cols` value if necessary.

    .. note::

       On this moment it's user responsibility to preprocess problem and build
       decomposition tree.

    :param problem: A problem to be solved.
    :param decomposition_tree: A :class:`les.decomposition_tree.DecompositionTree`
          instance that represents `problem` structure.

    :raises: TypeError
    """
    if not isinstance(problem, BILPProblem):
      raise TypeError()
    if not isinstance(decomposition_tree, DecompositionTree):
      raise TypeError("decomposition_tree must be derived from DecompositionTree")
    self._original_decomposition_tree = decomposition_tree
    self._decomposition_tree = decomposition_tree.copy()
    has_updates = True
    while has_updates:
      has_updates = False
      for node in self._decomposition_tree.get_nodes(data=True):
        # Instead of computing the total number of shared cols from edges we can
        # simply take this number directly from the problem
        subproblem = node[1].get("subproblem")
        if subproblem.get_num_shared_variables() <= max_num_shared_cols:
          continue
        edges = sorted(self._decomposition_tree.in_edges(node[0], data=True)
                     + self._decomposition_tree.out_edges(node[0], data=True),
                     key=lambda e: len(e[2].get("shared_cols")), reverse=True)
        self.logger.info("Merge subproblems %s and %s" % (edges[0][0], edges[0][1]))
        self._decomposition_tree.merge_nodes(edges[0][0], edges[0][1])
        has_updates = True
        break
    self._problem = problem

  def get_obj_value(self):
    """The objective function value of the current solution.

    :returns: An objective function value.
    """
    return self._obj_value
