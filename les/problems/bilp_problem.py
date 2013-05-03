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

"""In binary problems, each variable can only take on the value of 0 or 1. This
may represent the selection or rejection of an option, the turning on or off
of switches, a yes/no answer, or many other situations.

    :math:`f(x) = \\sum_{j=1}^{n}{c_{j}x_{j}}{ \\rightarrow max}`

        subject to

    :math:`\\sum_{j=1}^{n}{a_{ij}x_j \\leq b_i, \quad i=\\overline{1,m}},
    \quad x_j=\{0,1\}, \quad j=\\overline{1,n}`

The following snippet shows how to build BILP problem from scratch::

  problem = BILPProblem.build_from_scratch(
    # objective function
    ([8, 2, 5, 5, 8, 3, 9, 7, 6], True),
    # constraint matrix
    [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
     [1., 2., 3., 2., 0., 0., 0., 0., 0.],
     [0., 0., 1., 4., 3., 4., 2., 0., 0.],
     [0., 0., 2., 1., 1., 2., 5., 0., 0.],
     [0., 0., 0., 0., 0., 0., 2., 1., 2.],
     [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
    # right hand side
    [7, 6, 9, 7, 3, 5]
  )

Once the BILP problem has been defined it can be solved with help of one of the
:class:`~les.solvers.bilp_solver_base.BILPSolverBase` derived solvers.

"""

import os
import numpy as np
from scipy import sparse
import gzip
import types

from les.sparse_vector import SparseVector
from les.problems.problem_base import ProblemBase
from les.readers.mps_reader import MPSReader

_READERS = {
  ".mps": MPSReader
}

class BILPProblem(ProblemBase):
  """This class represents generic binary integer linear programming (BILP)
  problem model (or zero-one linear programming (ZOLP) problem).

  By default maximization is set.

  :param name: Optional string that represents problem name.
  """

  def __init__(self, name=None):
    ProblemBase.__init__(self, name)
    self._obj_coefs = None
    self._cons_matrix = None
    self._maximize = True
    self._cons_senses = []
    self._rhs = None

  def __str__(self):
    return "%s[num_rows=%d, num_cols=%d]" \
        % (self.__class__.__name__, self.get_num_rows(), self.get_num_cols())

  @property
  def maximize(self):
    return self._maximize

  @maximize.setter
  def maximize(self, true_or_false):
    if not true_or_false in (True, False):
      raise TypeError()
    self._maximize = true_or_false

  @classmethod
  def build(cls, *args, **kwargs):
    """Builds problem instance from already defined model. This method tries
    to define model type and apply correct build method, such as
    :func:`build_from_mps`.

    :returns: A :class:`BILPProblem` instance.

    :raises: IOError, TypeError
    """
    if len(args) > 1:
      return self.build_from_scratch(*args, **kwargs)
    model = args[0]
    if isinstance(model, MPSReader):
      return cls.build_from_mps(model)
    elif type(model) is types.StringType:
      # The file name has been provided. Detect reader and read the problem.
      if not os.path.exists(model):
        raise IOError("File doesn't exist: %s" % model)
      root, ext = os.path.splitext(model)
      if model.endswith(".gz"):
        stream = gzip.open(model, "rb")
        root, ext = os.path.splitext(root)
      else:
        stream = open(model, "r")
      reader_class = _READERS.get(ext)
      if not reader_class:
        raise Exception("Doesn't know how to read %s format."
                        "See available formats."
                        % ext)
      reader = reader_class()
      reader.parse(stream)
      stream.close()
      return cls.build(reader)
    else:
      raise TypeError("Don't know how to handle this model")

  @classmethod
  def build_from_scratch(cls, obj, cons_matrix=None, rhs=[]):
    """Builds BILP problem from a scratch.

    The following code snippet shows how to define two problems from scratch,
    where the first problem needs to be maximized and the second one --
    minimized::

      BILPProblem.build_from_scratch([1, 1, 2], [[1, 2, 3], [1, 1]])
      BILPProblem.build_from_scratch(([1, 1, 2], False), [[1, 2, 3], [1, 1]])

    :param obj: This parameter can be represented either a list of objective
      function variable coefficients, or a tuple, where the first element is
      a list of coefficients and the second one is ``True`` or ``False``, that
      defines objective function maximization or minimization. By default does
      maximization (see :func:`set_objective`).
    :param cons_matrix: A constraint matrix.
    :param rhs: A list of rhs bounds.

    :returns: A :class:`BILPProblem` instance.

    :raises: TypeError
    """
    import numpy
    problem = cls()
    if not isinstance(obj, tuple):
      problem.set_objective(obj)
    elif isinstance(obj, tuple) and len(obj) == 2:
      problem.set_objective(obj[0], obj[1])
    else:
      raise TypeError("obj has to be a list or a tuple: %s" % type(obj))
    problem._set_cons_matrix(cons_matrix)
    problem.set_rhs(rhs)
    return problem

  @classmethod
  def build_from_mps(cls, reader):
    """Builds a new BILP problem instance from MPS model.

    :param reader: A :class:`MPSReader` instance.

    :returns: A :class:`BILPProblem` instance.
    """
    # Build A from scratch. Use dok format.
    A = sparse.dok_matrix((len(reader._row_register), len(reader._col_register)),
                          dtype=np.float16)
    for i, j, v in reader.get_con_coefs():
      A[i, j] = v
    A = A.tocsr()
    rhs = reader.get_rhs()[0]
    if not len(rhs) == A.shape[0]:
      raise Exception()
    problem = BILPProblem.build_from_scratch(A[0,:].todense(), A[1:,:], rhs[1:])
    problem.set_name(reader.get_name())
    return problem

  def build_subproblem(self, *args, **kwargs):
    return BILPSubproblem(self, *args, **kwargs)

  def get_num_rows(self):
    """Counts the number of rows/constraints in the constraint matrix. All the
    columns are binary.

    :returns: An integer that represents number of rows.
    """
    return self._cons_matrix.shape[0]

  def get_num_cols(self):
    """Counts the number of columns/variables in the constraint matrix.

    :returns: The number of columns.
    """
    return self._cons_matrix.shape[1]

  def _set_cons_matrix(self, m):
    if isinstance(m, np.matrix):
      self._cons_matrix = sparse.csr_matrix(m)
    elif isinstance(m, list):
      self._cons_matrix = sparse.csr_matrix(np.matrix(m))
    else:
      self._cons_matrix = m

  def set_objective(self, coefs, maximize=True):
    """Set objective function."""
    if not maximize:
      raise NotImplementedError("minimization is not yet supported")
    if isinstance(coefs, (tuple, list)):
      obj = sparse.dok_matrix((1, len(coefs)), dtype=np.float16)
      for i, c in enumerate(coefs):
        obj[0, i] = c
    else:
      obj = coefs
    self._obj_coefs = SparseVector(obj)

  def get_obj_coefs(self):
    return self._obj_coefs

  def get_rhs(self):
    return self._rhs

  def set_row_upper_bound(self, i, v):
    """Set a single row upper bound."""
    self._rhs[i] = v

  def set_rhs(self, values):
    """Set rows upper bounds.

    :raises: TypeError
    """
    if isinstance(values, sparse.dok_matrix):
      self._rhs = SparseVector(values)
    elif isinstance(values, (tuple, list)):
      m = sparse.dok_matrix((1, len(values)), dtype=np.float16)
      for i, c in enumerate(values):
        m[0, i] = c
      self._rhs = SparseVector(m)
    elif isinstance(values, SparseVector):
      self._rhs = values
    else:
      raise TypeError()

  def get_cons_matrix(self):
    """Returns constraint matrix.

    :returns: A :class:`scipy.sparse.csr_matrix` instance. By default returns
      ``None``.
    """
    return self._cons_matrix

  def check_col_solution(self, solution):
    """Checks whether or not the given solution is correct.

    :param solution: A list of column values.

    :returns: `True` or `False`.
    """
    # TODO: solution can be a tuple, list or sparse.base.spmatrix
    if len(solution) != self.get_num_cols():
      raise Exception("%d != %d" % (solution.shape[1], self.get_num_cols()))
    v = self._cons_matrix.dot(solution)
    for i in xrange(len(v)):
      # TODO: add sense
      if v[i] > self._rhs[i]:
        return False
    return True

ZOLPProblem = BILPProblem

class BILPSubproblem(BILPProblem):
  """Subproblem name will be set automatically by solver."""

  def __init__(self, problem, obj_coefs=[], cons_matrix=None, rhs=[],
               maximize=True, shared_cols=[]):
    BILPProblem.__init__(self)
    self._name = None
    self._problem = problem
    self._shared_cols = shared_cols
    self._local_cols = set(cons_matrix.nonzero()[1]) - shared_cols
    self._nonzero_cols = self._shared_cols | self._local_cols
    self._deps = dict()
    # FIXME:
    self.set_objective(obj_coefs)
    self._set_cons_matrix(cons_matrix)
    self.set_rhs(rhs)

  def __str__(self):
    return "%s[num_shared_cols=%d, num_local_cols=%d]" \
        % (self._name, len(self._shared_cols), len(self._local_cols))

  def __add__(self, other):
    # Build objective function
    c1 = zip(*self.get_obj_coefs().keys())
    c2 = zip(*other.get_obj_coefs().keys())
    obj = SparseVector((1, self.get_num_cols()), dtype=np.float16)
    for u in (self.get_obj_coefs(), other.get_obj_coefs()):
      for ij, c in zip(u.keys(), u.values()):
        obj[ij[1]] = c
    # Build constraint matrix
    m1 = self.get_cons_matrix().tocoo()
    m2 = other.get_cons_matrix().tocoo()
    cons_matrix = sparse.coo_matrix(
      (m1.data.tolist() + m2.data.tolist(),
       zip(*(zip(m1.row, m1.col)
             + zip(map(lambda x: x + m1.shape[0], m2.row), m2.col)))),
      shape=(self.get_cons_matrix().shape[0] + other.get_cons_matrix().shape[0],
             self.get_cons_matrix().shape[1])
    )
    c1 = zip(*self.get_rhs().keys())
    c2 = zip(*other.get_rhs().keys())
    rhs = SparseVector((1, m1.shape[0] + m2.shape[0]), dtype=np.float16)
    for u in (self.get_rhs(), other.get_rhs()):
      offset = len(upper_bounds.values())
      for ij, c in zip(u.keys(), u.values()):
        rhs[ij[1] + offset] = c
    # Build the new problem
    return BILPSubproblem(
      self._problem,
      obj_coefs=obj, cons_matrix=cons_matrix.tocsr(),
      rhs=rhs,
      shared_cols=self.get_shared_cols() ^ other.get_shared_cols()
    )

  def get_shared_cols(self):
    """Returns a set of shared columns."""
    return self._shared_cols

  def get_num_shared_cols(self):
    """Returns number of shared columns."""
    return len(self._shared_cols)

  def get_local_cols(self):
    """Returns a set of local columns."""
    return self._local_cols

  def get_num_local_cols(self):
    """Returns number of local columns."""
    return len(self._local_cols)

  def get_dependencies(self):
    """Returns subproblem dependencies."""
    return self._deps

  def get_nonzero_cols(self):
    return self._nonzero_cols

  def add_dependency(self, subproblem, shared_cols):
    """Add subproblem dependency."""
    if not isinstance(shared_cols, set):
      raise TypeError("shared_cols must be a set")
    if not len(shared_cols):
      raise Exception("No shared cols")
    self._deps[subproblem] = shared_cols

  def remove_dependecy(self, other):
    if not isinstance(other, BILPProblem):
      raise TypeError()
    del self._deps[other]
