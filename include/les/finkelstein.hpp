/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file finkelstein.hpp
 * @brief Finkelstein algorithm.
 */

#ifndef __LES_FINKELSTEIN_DECOMPOSITION_HPP
#define __LES_FINKELSTEIN_DECOMPOSITION_HPP

#include <les/milp_problem.hpp>

class FinkelsteinQBDecomposition {
public:
  /** Empty constructor. */
  FinkelsteinQBDecomposition()
  {
  }

  void decompose(MILPP* problem,
                 vector<int>* initial_cols, vector<set<int>*>* U,
                 vector<set<int>*>* S, vector<set<int>*>* M);

  /**
   * Decompose a problem by using finkelstein algorithm on
   * blocks and return a chaine of DecompositionBlock. See also
   * decompose().
   */
  vector<DecompositionBlock*>* decompose_by_blocks(MILPP* problem);

private:
  MILPP* problem_;
  vector<set<int>*>* U_;
  vector<set<int>*>* S_;
  vector<set<int>*>* M_;
};

#endif /* __LES_FINKELSTEIN_DECOMPOSITION_HPP */
