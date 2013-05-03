************************
Local Elimination Solver
************************

This package represents local elimination solver (LES).

The following steps are required to use :class:`LocalEliminationSolver` to solve
the problem:

1. Define the problem.
2. Decompose the problem.
3. Setup the solver
4. Load the problem.
5. Solve the problem.

The following code snippet shows a simple case how you can use local elimination
solver to solve a given `problem`::

  from les.decomposers import FinkelsteinQBDecomposer
  from les.solvers import LocalEliminationSolver, \\
                          DummySolverFactory, \\
                          FractionalKnapsackSolverFactory, \\
                          OsiSymSolverInterfaceFactory, \\
                          OsiClpSolverInterfaceFactory

  # Decompose the problem
  decomposer = FinkelsteinQBDecomposer()
  decomposer.decompose(problem)
  # Setup the solver
  solver = LocalEliminationSolver()
  solver.set_params(
    master_solver_factory=OsiSymSolverInterfaceFactory(),
    relaxation_solver_factories=[
      DummySolverFactory(),
      FractionalKnapsackSolverFactory(),
      OsiClpSolverInterfaceFactory()
    ]
  )
  # Load the problem
  solver.load_problem(problem, decomposer.get_decomposition_tree())
  # Solve the problem
  solver.solve()

.. toctree::
   :maxdepth: 1

   les
