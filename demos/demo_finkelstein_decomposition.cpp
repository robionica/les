// Copyright (c) 2012 Alexander Sviridenko

#include <iostream>
#include <boost/foreach.hpp>

#include "demo_qbmilp_problem1.hpp"

#include "les/quasiblock_milp_problem.hpp"
#include "les/decomposers/finkelstein.hpp"

int main()
{
  DemoQBMILPProblem1 problem = DemoQBMILPProblem1();

  // Do finkelstein quasi-block decomposition and obtain decomposition
  // information
  FinkelsteinQBDecomposition decomposer;
  decomposer.decompose(&problem);
  cout << "Finkelstein decomposition information:" << endl;
  decomposer.dump();

  vector<QBMILPP*> subproblems = decomposer.get_subproblems();
  BOOST_FOREACH(QBMILPP* subproblem, subproblems) {
    subproblem->dump();
  }

  return 0;
}
