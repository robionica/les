/*
 * Copyright (c) 2012 Alexander Sviridenko
 */
#ifndef __OSI_LESOLVER_INTERFACE_HPP
#define __OSI_LESOLVER_INTERFACE_HPP

/* Inlcude LES API */
#include <les/solver.hpp>
/* Include native symphony API */
#include <coin/OsiSymSolverInterface.hpp>

using namespace std;

class OsiLeSolverInterface : public Solver {
public:
  OsiLeSolverInterface() : _obj_value(0.) {}

  void solve(vector<DecompositionBlock*>* blocks);
  void solve_block(DecompositionBlock* block);

  inline double get_col_value(int i)
  {
    assert(i < solution_.size());
    return solution_[i];
  }
  const vector<double>* get_solution() { return &solution_; }

  /** Return objective function value. */
  double get_obj_value();

private:
  double _obj_value;
  vector<double> solution_;
};

#endif /* __OSI_LESOLVER_INTERFACE_HPP */
