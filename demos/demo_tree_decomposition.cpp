/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <les/decomposition.hpp>

int
main()
{
  Graph g;
  for (int i = 0; i < 9; i++)
    g.add_vertex(i);
  g.add_edge(0, 2);
  g.add_edge(0, 4);
  g.add_edge(0, 4);
  g.add_edge(1, 2);
  g.add_edge(1, 4);
  g.add_edge(0, 4);
  g.add_edge(1, 8);
  g.add_edge(4, 3);
  g.add_edge(4, 8);
  g.add_edge(8, 5);
  g.add_edge(5, 7);
  g.add_edge(5, 7);
  g.add_edge(6, 7);
  g.dump();

  PermutationToTreeDecomposition decomposer;
  int order[] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
  vector<int> permutation(order, order + sizeof(order) / sizeof(int));
  decomposer.decompose(g, permutation);
  decomposer.dump();

  return 0;
}
