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

  import operator
  import les

  problem = les.BILPProblem('PROBLEM', (
    # objective function
    ([8, 2, 5, 5, 8, 3, 9, 7, 6], True),
    # left-hand size
    [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
     [1., 2., 3., 2., 0., 0., 0., 0., 0.],
     [0., 0., 1., 4., 3., 4., 2., 0., 0.],
     [0., 0., 2., 1., 1., 2., 5., 0., 0.],
     [0., 0., 0., 0., 0., 0., 2., 1., 2.],
     [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
    # senses
    [operator.le] * 6,
    # right-hand side
    [7, 6, 9, 7, 3, 5]
  ))
  print problem

Prints ``BILPProblem[name=PROBLEM, num_constraints=6, num_variables=9]``. Or
another way define the same problem model::

  problem = les.BILPProblem('PROBLEM', (
    8*x1 + 2*x2 + 5*x3 + 5*x4 + 8*x5 + 3*x6 + 9*x7 + 7*x8 + 6*x9,
    [2*x1 + 3*x2 + 3*x3 +   x4 <= 7,
       x1 + 2*x2 + 3*x3 + 2*x4 <= 6,
                     x3 + 4*x4 + 3*x5 + 4*x6 + 2*x7 <= 9,
                   2*x3 +   x4 +   x5 + 2*x6 + 5*x7 <= 7,
                                               2*x7 +   x8 + 2*x9 <= 3,
                                               3*x7 + 4*x8 +   x9 <= 5]
  ))

Once the BILP problem has been defined it can be solved with help of one of the
:class:`~les.solvers.bilp_solver_base.BILPSolverBase` derived solvers.
"""

import os
import operator
import numpy as np
import gzip
import types

from les.problems.problem_base import ProblemBase
from les.readers.mps_reader import MPSReader
from les.ext.scipy import sparse

STD_SENSE_STR_TO_OPERATOR = {
  'L': operator.le,
  'G': operator.ge,
  'E': operator.eq,
}

_READERS = {
  ".mps": MPSReader
}

class BILPProblem(ProblemBase):
  """This class represents generic binary integer linear programming (BILP)
  problem model (or zero-one linear programming (ZOLP) problem).

  By default maximization is set.

  This implementation allows you to use operators such as :class:`operator.le`,
  :class:`operator.ge` from :mod:`operator` as senses for constraints in your
  problem model.

  :param name: Optional string that represents problem name.
  """

  def __init__(self, name=None, model=None):
    ProblemBase.__init__(self, name)
    self._obj = None
    self._maximize = True
    self._lhs = None
    self._cons = []
    self._rhs = None
    if model:
      if isinstance(model, tuple):
        self.read(*model)
      else:
        self.read(model)

  def __str__(self):
    return "%s[name=%s, num_constraints=%d, num_variables=%d]" \
        % (self.__class__.__name__, self.get_name(),
           self.get_num_constraints(), self.get_num_variables())

  @property
  def constraints(self):
    """This property provides access to constraints.

    The following code snippet shows an easy way to change bound of the first
    constraint of the problem::

      problem.constraints[0].rhs = 9.0
    """
    return self._cons

  @property
  def maximize(self):
    return self._maximize

  @maximize.setter
  def maximize(self, true_or_false):
    if not true_or_false in (True, False):
      raise TypeError()
    self._maximize = true_or_false

  def read(self, *args, **kwargs):
    """The general entry point to initialize this problem from predefined model
    object or file name.

    If the model name is represented by a string, then the type of data read is
    determined by the file suffix.
    """
    if len(args) > 1:
      self.read_from_scratch(*args, **kwargs)
    else:
      raise Exception

  def read_from_scratch(self, obj, lhs, senses, rhs):
    """Reads BILP problem from a scratch.

    :param obj: This parameter can be represented either a list of objective
      function variable coefficients, or a tuple, where the first element is
      a list of coefficients and the second one is ``True`` or ``False``, that
      defines objective function maximization or minimization. By default does
      maximization (see :func:`set_objective`).
    :param lhs: Left-hand side or constraint matrix.
    :param senses: A list/tuple of constraint senses.
    :param rhs: Right-hand side or a list of constraint bounds.
    """
    if not isinstance(obj, tuple):
      self.set_objective(obj)
    elif isinstance(obj, tuple) and len(obj) == 2:
      self.set_objective(obj[0], obj[1])
    else:
      raise TypeError("obj has to be a list or a tuple: %s" % type(obj))
    self._set_lhs(lhs)
    self._set_rhs(rhs)

  def write(self, filename):
    """Writes model data to the file.

    :param filename: A string that represents file name.
    """
    raise NotImplementedError()

  @classmethod
  def build(cls, *args, **kwargs):
    """Builds problem instance from already defined model. This method tries
    to define model type and apply correct build method, such as
    :func:`build_from_mps`.

    :returns: A :class:`BILPProblem` instance.

    :raises: :exc:`IOError`, :exc:`TypeError`

    .. seealso:: :func:`build_from_mps`, :func:`build_from_scratch`
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
  def build_from_scratch(cls, obj, lhs, senses, rhs):
    """Builds BILP problem from a scratch.

    The following code snippet shows how to define two problems from scratch,
    where the first problem needs to be maximized and the second one --
    minimized::

      BILPProblem.build_from_scratch([1, 1, 2], [[1, 2, 3], ['L', 'L'], [1, 1]])
      BILPProblem.build_from_scratch(([1, 1, 2], False), [[1, 2, 3], ['L', 'L'], [1, 1]])

    :param obj: This parameter can be represented either a list of objective
      function variable coefficients, or a tuple, where the first element is
      a list of coefficients and the second one is ``True`` or ``False``, that
      defines objective function maximization or minimization. By default does
      maximization (see :func:`set_objective`).
    :param lhs: Left-hand side or constraint matrix.
    :param senses: A list of senses of the constraints.
    :param rhs: A list of rhs bounds.
    :returns: A :class:`BILPProblem` instance.

    :raises: :exc:`TypeError`

    .. seealso:: :func:`read_from_scratch`
    """
    problem = cls()
    problem.read_from_scratch(obj, lhs, senses, rhs)
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
    for i, j, v in reader.get_lhs():
      A[i, j] = v
    A = A.tocsr()
    rhs = reader.get_rhs()[0]
    if not len(rhs) == A.shape[0]:
      raise Exception()
    problem = BILPProblem.build_from_scratch(
      A[0,:].todense(),
      A[1:,:],
      reader.get_row_senses()[1:],
      rhs[1:]
    )
    problem.set_name(reader.get_name())
    return problem

  def build_subproblem(self, *args, **kwargs):
    return BILPSubproblem(self, *args, **kwargs)

  def get_num_constraints(self):
    """Counts the number of constraints/rows in the constraint matrix.

    :returns: An integer that represents number of rows.
    """
    return self._lhs.shape[0]

  def get_num_variables(self):
    """Counts the number of variables/cols in the constraint matrix. All the
    variables are binary.

    :returns: The number of variables.
    """
    return self._lhs.shape[1]

  def get_constraints(self):
    """Returns the list of constraints."""
    return self._cons

  def set_constraints(self, *args):
    """Set constraints.

    :param lhs: Left-hand side. Can be represented by a sparse matrix.
    :param senses: A list/tuple of senses of the constraints.
    :param rhs: Right-hand side. Can be represented by a list, tuple or vector.
    :param optional names: A list/tuple of names for new constraints.

    .. note:: The number of elements in `lhs`, `senses`, `rhs` and `names` must
              be the same.

    The following code snippet shows a way to set constraints to the new
    problem::

      import operator

      problem.set_constraints(
        [[1, 2, 3], [4, 5, 6]],
        [operator.le, operator.le],
        [3, 9]
      )
      # or the same
      problem.set_constraints([[1, 2, 3], [4, 5, 6]], ['L', 'L'], [3, 9])
    """
    if len(args) > 2:
      if len(args) == 3:
        lhs, senses, rhs = args
        if len(lhs) != len(senses) or len(senses) != len(rhs):
          raise Exception()
      elif len(args) == 4:
        lhs, senses, rhs, names = args
      else:
        raise Exception()
      self._set_lhs(lhs)
      senses = self._convert_senses(senses)
      self._set_rhs(rhs)
    else:
      raise Exception()

  def _convert_senses(self, senses):
    if not type(senses) in (list, tuple):
      raise TypeError()
    for i in range(len(senses)):
      if isinstance(senses[i], str):
        senses[i] = STD_SENSE_STR_TO_OPERATOR[senses[i]]
    return senses

  def set_objective(self, coefs, maximize=True):
    """Set the problem objective function.

    :param coefs: Coefs.
    :param optional maximize: Boolean that defines whether or not we need to do
      maximization.

    Example usage::

      problem.set_objective([1, 2])
      problem.set_objective([3, 4, 5], False)
    """
    if not maximize:
      raise NotImplementedError("minimization is not yet supported")
    if isinstance(coefs, (tuple, list)):
      obj = sparse.dok_matrix((1, len(coefs)), dtype=np.float16)
      for i, c in enumerate(coefs):
        obj[0, i] = c
    else:
      obj = coefs
    self._obj = sparse.dok_vector(obj)

  def get_objective(self):
    """Returns objective."""
    return self._obj

  def get_rhs(self):
    """Returns vector that represents right-hand side."""
    return self._rhs

  def set_row_upper_bound(self, i, v):
    """Set a single row upper bound."""
    self._rhs[i] = v

  def _set_rhs(self, values):
    """Set right-hand side -- constraint bounds."""
    if isinstance(values, sparse.dok_matrix):
      self._rhs = sparse.dok_vector(values)
    elif isinstance(values, (tuple, list)):
      m = sparse.dok_matrix((1, len(values)), dtype=np.float16)
      for i, c in enumerate(values):
        m[0, i] = c
      self._rhs = sparse.dok_vector(m)
    elif isinstance(values, sparse.dok_vector):
      self._rhs = values
    else:
      raise TypeError()

  def get_lhs(self):
    """Returns left-hand side represented by constraint matrix.

    :returns: A :class:`scipy.sparse.csr_matrix` instance. By default returns
      ``None``.
    """
    return self._lhs

  def _set_lhs(self, m):
    if isinstance(m, np.matrix):
      self._lhs = sparse.csr_matrix(m)
    elif isinstance(m, list):
      self._lhs = sparse.csr_matrix(np.matrix(m))
    else:
      self._lhs = m

  def check_col_solution(self, solution):
    """Checks whether or not the given solution is correct.

    :param solution: A list of column values.

    :returns: ``True`` or ``False``.
    """
    # TODO: solution can be a tuple, list or sparse.base.spmatrix
    if len(solution) != self.get_num_variables():
      raise Exception("%d != %d" % (solution.shape[1], self.get_num_variables()))
    v = self._lhs.dot(solution)
    for i in xrange(len(v)):
      # TODO: add sense
      if v[i] > self._rhs[i]:
        return False
    return True

BILPProblem.get_num_columns = BILPProblem.get_num_variables
BILPProblem.get_num_rows = BILPProblem.get_num_constraints

ZOLPProblem = BILPProblem

class BILPSubproblem(BILPProblem):
  """This class represents BILP problem subproblem.

  Subproblem name will be set automatically by solver.

  :param problem: Source :class:`BILPProblem` problem instance.
  :param shared_variables: A set of shared variables.
  """

  def __init__(self, problem, obj_coefs=[], lhs=None, rhs=[],
               maximize=True, shared_variables=[]):
    BILPProblem.__init__(self)
    self._problem = problem
    self._shared_vars = shared_variables
    self._local_vars = set(lhs.nonzero()[1]) - shared_variables
    self._nonzero_vars = self._shared_vars | self._local_vars
    self._deps = dict()
    # FIXME:
    self.set_objective(obj_coefs)
    self._set_lhs(lhs)
    self._set_rhs(rhs)

  def __str__(self):
    return "%s[num_shared_variables=%d, num_local_variables=%d]" \
        % (self._name, len(self._shared_vars), len(self._local_vars))

  def __add__(self, other):
    # Build objective function
    c1 = zip(*self.get_obj_coefs().keys())
    c2 = zip(*other.get_obj_coefs().keys())
    obj = sparse.dok_vector((1, self.get_num_columns()), dtype=np.float16)
    for u in (self.get_obj_coefs(), other.get_obj_coefs()):
      for ij, c in zip(u.keys(), u.values()):
        obj[ij[1]] = c
    # Build constraint matrix
    m1 = self.get_lhs().tocoo()
    m2 = other.get_lhs().tocoo()
    cons_matrix = sparse.coo_matrix(
      (m1.data.tolist() + m2.data.tolist(),
       zip(*(zip(m1.row, m1.col)
             + zip(map(lambda x: x + m1.shape[0], m2.row), m2.col)))),
      shape=(self.get_lhs().shape[0] + other.get_lhs().shape[0],
             self.get_lhs().shape[1])
    )
    c1 = zip(*self.get_rhs().keys())
    c2 = zip(*other.get_rhs().keys())
    rhs = sparse.dok_vector((1, m1.shape[0] + m2.shape[0]), dtype=np.float16)
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

  def get_shared_variables(self):
    """Returns a set of shared variables."""
    return self._shared_vars

  def get_num_shared_variables(self):
    """Returns number of shared variables."""
    return len(self._shared_vars)

  def get_local_variables(self):
    """Returns a set of local variables."""
    return self._local_vars

  def get_num_local_variables(self):
    """Returns number of local variables."""
    return len(self._local_vars)

  def get_dependencies(self):
    """Returns subproblem dependencies."""
    return self._deps

  def get_nonzero_variables(self):
    """Returns a set of nonzero variables."""
    return self._nonzero_vars

  def add_dependency(self, other, shared_variables):
    """Add subproblem dependency.

    :param other: A :class:`BILPSubproblem` instance.
    :param shared_variables: A set of shared variables.

    :raises: :exc:`TypeError`
    """
    if not isinstance(shared_variables, set):
      raise TypeError("shared_variables must be a set")
    if not len(shared_variables):
      raise Exception("No shared variables")
    self._deps[other] = shared_variables

  def remove_dependecy(self, other):
    """Removes dependency.

    :param other: A :class:`BILPSubproblem` instance.

    :raises: TypeError
    """
    if not isinstance(other, BILPProblem):
      raise TypeError()
    del self._deps[other]
