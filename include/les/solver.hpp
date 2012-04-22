/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file solver.hpp
 * @brief Generic solver interface.
 */

#ifndef __LES_SOLVER_HPP
#define __LES_SOLVER_HPP

#include <les/quasiblock_milp_problem.hpp>

class Solver {
public:
  void initial_solve();

  /* Slave solver */
  void* get_slave_solver() { return slave_solver; }

  /** @name Problem manipulations. */
  /** @{ */

  /** Load problem. */
  void load_problem(Problem* problem);

  /** @} */

  /** @name Objective function methods. */
  /** @{ */

  /** Get objective function value. */
  double get_obj_value();

  /* Columns */
  const double* get_col_solution();

  /** @} */

protected:
  void* slave_solver;
};

#endif /* __LES_SOLVER_HPP */

