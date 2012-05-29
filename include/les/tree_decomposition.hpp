/*
 * Copyright (c) 2012 Alexander Sviridenko
 */
#ifndef __LES_TREE_DECOMPOSITION_HPP
#define __LES_TREE_DECOMPOSITION_HPP

#include <les/interaction_graph.hpp>
#include <les/decomposition.hpp>

class PermutationToTreeDecomposition
{
public:
  PermutationToTreeDecomposition()
  {
  }

  /** Build a tree decomposition of the input graph amd given
      permutation. */
  void decompose(const InteractionGraph& g,
                 const vector<int>& permutation);

  const vector<int>& get_permutation() { return _permutation; }

private:
  void decompose(vector<int>& permutation, int permutation_index);

  vector<int> _permutation;
  boost::graph_t _decomposition_tree;
};



#endif /* __LES_TREE_DECOMPOSITION_HPP */
