// Copyright (c) 2012 Alexander Sviridenko

//
// How to use:
//
// MILPP* problem = new MILPP();
// ...
//
// FinkelsteinQBDecomposition* decomposer = new FinkelsteinQBDecomposition();
// vector<DecompositionBlock*>* blocks = decomposer->decompose_by_blocks(problem);
//

/**
 * @file finkelstein.hpp
 * @brief Finkelstein algorithm.
 */

#ifndef __LES_DECOMPOSITION_FINKELSTEIN_HPP
#define __LES_DECOMPOSITION_FINKELSTEIN_HPP

#include <les/milp_problem.hpp>
#include <les/decomposition.hpp>
#include <les/interaction_graph.hpp>

class FinkelsteinQBDecomposition {
public:
  // Empty constructor
  FinkelsteinQBDecomposition()
  {
  }

  void decompose(MILPP* problem,
                 vector<int>* initial_cols, vector<set<int> >* U,
                 vector<set<int> >* S, vector< set<int> >* M,
                 int max_separator_size = 0,
                 bool merge_empty_blocks = true);

  // Decompose a problem by using finkelstein algorithm on blocks and return a
  // chaine of DecompositionBlock. See also decompose().
  vector<DecompositionBlock*>* decompose_by_blocks(MILPP* problem);

  void dump();

private:
  MILPP* _problem;
  vector< set<int> > _U;
  vector< set<int> > _S;
  vector< set<int> > _M;
};

#endif // __LES_DECOMPOSITION_FINKELSTEIN_HPP
