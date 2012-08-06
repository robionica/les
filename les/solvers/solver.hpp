// Copyright (c) 2012 Alexander Sviridenko

#ifndef __LES_SOLVER_HPP
#define __LES_SOLVER_HPP

#include <les/quasiblock_milp_problem.hpp>

class Solver {
public:
  void solve();

  // Load problem.
  void load_problem(Problem* problem);
};

class MILPSolver : Solver {
public:
  // Get objective function value.
  inline double get_obj_value() {
    return _obj_value;
  }

  // Columns
  const double* get_col_solution();

private:
  double _obj_value;
  vector<double> solution_;
};

#endif // __LES_SOLVER_HPP