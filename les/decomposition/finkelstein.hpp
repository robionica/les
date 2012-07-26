// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied.  See the License for the specific language governing
// permissions and limitations under the License.

// How to use:
//
// MILPP* problem = new MILPP();
// ...
//
// FinkelsteinQBDecomposition decomposer;
// decomposer.decompose(problem);
// vector<QBMILPP*> subproblems = decomposer.get_subproblems();

/**
 * @file finkelstein.hpp
 * @brief Finkelstein algorithm.
 */

#ifndef __LES_DECOMPOSITION_FINKELSTEIN_HPP
#define __LES_DECOMPOSITION_FINKELSTEIN_HPP

#include <les/quasiblock_milp_problem.hpp>
#include <les/decomposition.hpp>
#include <les/interaction_graph.hpp>

class FinkelsteinQBDecomposition {
public:
  // Empty constructor
  FinkelsteinQBDecomposition()
  {
  }

  vector<QBMILPP*> get_subproblems();

  void decompose(MILPP* problem = NULL,
                 vector<int>* initial_cols = NULL,
                 vector<set<int> >* U = NULL, vector<set<int> >* S = NULL,
                 vector< set<int> >* M = NULL,
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

#endif  // __LES_DECOMPOSITION_FINKELSTEIN_HPP
