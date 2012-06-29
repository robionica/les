// Copyright (c) 2012 Alexander Sviridenko

/**
 * @file solver.hpp
 * @brief Generic solver interface.
 */

#ifndef __LES_SOLVER_HPP
#define __LES_SOLVER_HPP

#include <les/quasiblock_milp_problem.hpp>

class Solver {
public:
  void solve();

  // Load problem.
  void load_problem(Problem* problem);
};

class MasterSolver : Solver {
public:
  // Slave solver
  void* get_slave_solver() { return slave_solver; }

protected:
  void* slave_solver;
};

class MILPPSolverInterface {
public:
  // Get objective function value.
  double get_obj_value();

  // Columns
  const double* get_col_solution();
};

#endif /* __LES_SOLVER_HPP */
