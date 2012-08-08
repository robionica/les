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

  Symphony* symphony = new Symphony();
  symphony->load_problem(&problem);

  return 0;
}
