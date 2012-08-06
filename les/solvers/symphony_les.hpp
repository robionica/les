// Copyright (c) 2012 Alexander Sviridenko

#ifndef __LES_BSOLVERS_SYMPHONY_HPP
#define __LES_BSOLVERS_SYMPHONY_HPP

#include "les/bsolvers/bsolver.hpp"
// Include native symphony API
#include <coin/OsiSymSolverInterface.hpp>

using namespace std;

class Symphony : public BSolver {
public:
  // Empty constructor
  OsiLeSolverInterface() : _obj_value(0.) {}

  // Solve the problem decomposed by blocks. Optionally can be used relaxation.
  void solve(vector<DecompositionBlock*>* blocks, bool use_relaxation);
  void solve(vector<DecompositionBlock*>* blocks);
  void solve_with_relaxation(vector<DecompositionBlock*>* blocks);

  // Solve a single block. Note the solving information will be written in
  // block.
  void solve_block(DecompositionBlock* block);

  inline double get_col_value(int i)
  {
    assert(i < solution_.size());
    return solution_[i];
  }

  const vector<double>* get_solution() { return &solution_; }

  // Return objective function value.
  double get_obj_value();

private:
  double _obj_value;
  vector<double> solution_;
};

#endif // __LES_BSOLVERS_SYMPHONY_HPP
