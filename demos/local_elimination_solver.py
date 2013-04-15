#!/usr/bin/env python
#
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

from __future__ import print_function

import sys
import time
import numpy as np

from les.problems import BILPProblem
from les.solvers import LocalEliminationSolver
from les.decomposers import FinkelsteinQBDecomposer
from les.solvers import \
    LocalEliminationSolver, \
    DummySolverFactory, \
    FractionalKnapsackSolverFactory, \
    OsiSymSolverInterfaceFactory, OsiClpSolverInterfaceFactory

class _OsiClpSolverInterfaceFactory(OsiClpSolverInterfaceFactory):

  def build(self):
    si = OsiClpSolverInterfaceFactory.build(self)
    si.set_log_level(0) # switch off printout
    return si

class _OsiSymSolverInterfaceFactory(OsiSymSolverInterfaceFactory):

  def __init__(self):
    OsiSymSolverInterfaceFactory.__init__(self)

  def begin_first_iteration(self):
    self.si = OsiSymSolverInterfaceFactory.build(self)
    self.si.set_sym_param("verbosity", -2)

  def end_first_iteration(self):
    pass

  def build(self):
    self.si.reset()

def solve(problem):
  # Decompose the problem
  start = time.clock()
  decomposer = FinkelsteinQBDecomposer()
  decomposer.decompose(problem)
  end = time.clock()
  print("Decomposition time: %6.4f second(s)" % (end - start))
  # Solving...
  start = time.clock()
  solver = LocalEliminationSolver()
  solver.set_params(
    master_solver_factory=OsiSymSolverInterfaceFactory(params={"verbosity": -2}),
    relaxation_solver_factories=[
      DummySolverFactory(),
      FractionalKnapsackSolverFactory(),
      _OsiClpSolverInterfaceFactory()
    ]
  )
  solver.load_problem(problem, decomposer.get_decomposition_tree())
  solver.solve()
  end = time.clock()
  print("Solving time: %6.4f second(s)" % (end - start))
  print("Objective value:", solver.get_obj_value())
  print("Col solution:", solver.get_col_solution())

def main():
  if len(sys.argv) < 2:
    print("USAGE: %s FILENAME" % sys.argv[0], file=sys.stderr)
    print()
    print("Please provide input problem.", file=sys.stderr)
    exit(0)
  try:
    # Build the problem
    start = time.clock()
    problem = BILPProblem.build(sys.argv[1])
    end = time.clock()
    print("Build time: %6.4f second(s)" % (end - start))
    solve(problem)
  except KeyboardInterrupt, e:
    print("Interrupting...", file=sys.stderr)

if __name__ == "__main__":
  main()
