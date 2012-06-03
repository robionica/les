/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <les/decomposition.hpp>

int
main()
{
  Graph g;
  for (int i = 0; i < 8; i++)
    g.add_vertex(i);
  g.add_edge(0, 1);
  g.add_edge(1, 2);
  g.add_edge(0, 3);
  g.add_edge(3, 4);
  g.add_edge(0, 4);
  g.add_edge(1, 5);
  g.add_edge(4, 5);
  g.add_edge(4, 6);
  g.add_edge(6, 7);
  g.add_edge(4, 7);
  g.dump();

  PermutationToTreeDecomposition decomposer;
  //int order[] = {5, 2, 1, 0, 3, 4, 6, 7};
  int order[] = {7, 2, 1, 3, 5, 4, 6, 0};
  vector<int> permutation(order, order + sizeof(order) / sizeof(int));
  decomposer.decompose(g, permutation);
  decomposer.dump();

  return 0;
}
