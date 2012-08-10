// Copyright (c) 2012 Alexander Sviridenko

#ifndef __LES_SOLVERS_SYMPHONY_HPP
#define __LES_SOLVERS_SYMPHONY_HPP

// Include native symphony API
#include <coin/OsiSymSolverInterface.hpp>

#include <les/solvers/solver.hpp>

class Symphony : public MILPSolver
{
public:
  Symphony() {
    _si.setSymParam(OsiSymVerbosity, -2);
  }
  ~Symphony() {}

  void load_problem(MILPP* problem);

  inline void solve() {
    // Branch and bound method
    _si.branchAndBound();
  }

  inline double get_obj_value() {
    return _si.getObjValue();
  }

  inline const double* get_col_solution() {
    return _si.getColSolution();
  }

private:
  // Symphony interface
  OsiSymSolverInterface _si;
  // Problem
  MILPP* _problem;
};

#endif // __LES_SOLVERS_SYMPHONY_HPP
