/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <iostream>

#include <les/solvers/knapsack_problem_solver.hpp>

int
main()
{
  int v[] = {50, 140, 60, 60};
  int w[] = { 5, 20,  10, 12};
  int n = 4;
  int W = 30;
  FractionalKnapsackSolver* solver = new FractionalKnapsackSolver(v, w, n, W);
  solver->solve();
  cout << "Bag weight: " << solver->get_bag_weight() << endl;
  cout << "Bag value: " << solver->get_bag_value() << endl;
  map<int, double>& items = solver->get_bag_items();
  cout << "Items: " << endl;
  for (map<int, double>::iterator it = items.begin(); it != items.end(); it++) {
    cout << (*it).first << " ==> " << (*it).second << endl;
  }
  MILPP* problem = solver->get_problem();
  if (problem) {
    problem->dump();
  }
  delete solver;
  return 0;
}
