// Copyright (c) 2012 Alexander Sviridenko

#include <iostream>

#include <les/knapsack.hpp>

int
main()
{
  // Knapsack problem
  int v[] = {50, 140, 60, 60};
  int w[] = { 5,  20, 10, 12};
  int n = 4;
  int W = 30;

  FraktionalKnapsack* fk = new FraktionalKnapsack(v, w, n, W);
  cout << fk->get_bag_weight() << endl;

  return 0;
}
