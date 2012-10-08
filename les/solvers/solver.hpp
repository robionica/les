/*
 * Copyright (c) 2012 Oleksander Sviridenko
 */

#ifndef __LES_SOLVERS_SOLVER_HPP
#define __LES_SOLVERS_SOLVER_HPP

#include <les/quasiblock_milp_problem.hpp>

class Solver {
public:
  void solve();

  /**
   * Load problem.
   */
  void load_problem(Problem* problem);
};

class MILPSolver : Solver {
public:
  /**
   * Returns objective function value.
   */
  inline double get_obj_value() {
    return _obj_value;
  }

  /**
   * Returns array of columns.
   */
  const double* get_col_solution();

private:
  double _obj_value;
  vector<double> _solution;
};

#endif /* __LES_SOLVERS_SOLVER_HPP */
