/*
 * Solve the problem 1 with help of SYMPHONY
 *
 * Copyright (c) 2012 Oleksander Sviridenko
 */

#include <iostream>

#include "demo_milp_problem1.hpp"

#include "les/solvers/symphony.hpp"

int main()
{
  /* Problem */
  DemoMILPProblem1 problem = DemoMILPProblem1();
  cout << "Initial problem:" << endl;
  problem.dump();
  /* Solving */
  SymphonyWrapper solver;
  solver.load_problem(&problem);
  solver.solve();
  cout << "Objective value = " << solver.get_obj_value() << endl;
  cout << "Solution: ";
  for (int i = 0; i < problem.get_num_cols(); i++) {
    cout << solver.get_col_solution()[i] << " ";
  }
  cout << endl;
  return 0;
}
