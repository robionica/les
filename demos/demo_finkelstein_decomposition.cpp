/*
 * Demo finkelsteain decomposition
 *
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <iostream>
#include <boost/foreach.hpp>

#include "demo_qbmilp_problem1.hpp"

#include "les/quasiblock_milp_problem.hpp"
#include "les/decomposers/finkelstein.hpp"

int main()
{
  /* Problem */
  DemoQBMILPProblem1 problem = DemoQBMILPProblem1();
  cout << "Initial problem:" << endl;
  problem.dump();
  /*
   * Do finkelstein quasi-block decomposition and obtain decomposition
   * information
   */
  FinkelsteinQBDecomposition decomposer;
  decomposer.decompose(&problem);
  cout << "Finkelstein decomposition information:" << endl;
  decomposer.dump();
  vector<QBMILPP*> subproblems = decomposer.get_subproblems();
  BOOST_FOREACH(QBMILPP* subproblem, subproblems) {
    cout << "Subproblem:" << endl;
    subproblem->dump();
  }
  return 0;
}
