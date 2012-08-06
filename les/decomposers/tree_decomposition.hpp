/*
 * Copyright (c) 2012 Alexander Sviridenko
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied.  See the License for the specific language governing
 * permissions and limitations under the License.
 */

/**
 * @file tree_decomposition.hpp
 * @brief Tree decomposition algorithm
 */

#ifndef __LES_TREE_DECOMPOSITION_HPP
#define __LES_TREE_DECOMPOSITION_HPP

#include <les/graph.hpp>
#include <les/decomposition.hpp>

#include <map>

/**
 * This algorithm is a recursive procedure that builds a tree
 * decomposition from a permutation.
 */
class PermutationToTreeDecomposition
{
public:

  typedef vector<int> Bag;

  PermutationToTreeDecomposition()
  {
  }

  /** Build a tree decomposition of the input graph amd given
      permutation. */
  void decompose(Graph& g, const vector<int>& permutation);

  const vector<int>& get_permutation() { return _permutation; }

  void dump();

private:
  void decompose(const vector<int>& permutation, int permutation_index);

  vector<Bag> _bags;
  vector<int> _permutation;
  map<int, int> vertex_permutation_index;
  Graph* _g; /* pointer to original graph */
  Graph _h; /* temporary graph */
  Graph _decomposition_tree;
};

#endif /* __LES_TREE_DECOMPOSITION_HPP */
