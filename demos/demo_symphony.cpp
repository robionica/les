// Copyright (c) 2012 Alexander Sviridenko

#include <iostream>

#include "demo_qbmilp_problem1.hpp"

#include "les/solvers/symphony.hpp"

int main()
{
  // Problem
  DemoQBMILPProblem1 problem = DemoQBMILPProblem1();
  cout << "Initial problem:" << endl;
  problem.dump();

  Symphony solver;
  solver.load_problem(&problem);
  solver.solve();

  cout << "Objective value = " << solver.get_obj_value() << endl;
  cout << "Solution: ";

  for (int i = 0; i < problem.get_num_cols(); i++)
    cout << solver.get_col_solution()[i]
	 << " ";
  cout << endl;

  return 0;
}
