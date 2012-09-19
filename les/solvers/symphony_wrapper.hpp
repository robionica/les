// Copyright (c) 2012 Alexander Sviridenko

#ifndef __LES_SOLVERS_SYMPHONY_WRAPPER_HPP
#define __LES_SOLVERS_SYMPHONY_WRAPPER_HPP

// Include native symphony API
#include <coin/OsiSymSolverInterface.hpp>

#include <les/solvers/solver.hpp>

class SymphonyWrapper : public MILPSolver, public OsiSymSolverInterface
{
public:
  void load_problem(MILPP* problem);

  inline void solve() {
    // Temporary solution to make solver not so verbose.
    setSymParam(OsiSymVerbosity, -2);
    branchAndBound();
  }

  inline double get_obj_value() {
    return getObjValue();
  }

  inline const double* get_col_solution() {
    return getColSolution();
  }


private:
  // Problem
  MILPP* _problem;
};

#endif // __LES_SOLVERS_SYMPHONY_WRAPPER_HPP
