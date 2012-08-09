// Copyright (c) 2012 Alexander Sviridenko

#include <coin/CoinPackedVector.hpp>
#include <coin/CoinPackedMatrix.hpp>

#include "les/solvers/symphony.hpp"
#include <stdio.h>
void Symphony::load_problem(MILPP* problem)
{
  _problem = problem;

  // Add variables to the objective function and constraint matrix
  for (int i = 0; i < _problem->get_num_cols(); i++) {
    // Add a new variable
    CoinPackedVector col;
    _si.addCol(col, 0.0, 1.0, _problem->get_obj_coef(i));
    // Set variable type
    _si.setInteger(i);
  }
  // Add constraints
  for (int i = 0; i < _problem->get_num_rows(); i++) {
    PackedVector* source_row = _problem->get_row(i);
    CoinPackedVector target_row(_problem->get_num_cols(),
				source_row->get_elements());
    _si.addRow(target_row, 'L', _problem->get_row_upper_bound(i), 1.0);
  }
  // Set problem sense
  _si.setObjSense(_problem->get_obj_sense());
}
