// Copyright (c) 2012 Alexander Sviridenko

#include <coin/CoinPackedVector.hpp>
#include <coin/CoinPackedMatrix.hpp>

#include "les/solvers/symphony.hpp"

void SymphonyWrapper::load_problem(MILPP* problem)
{
  _problem = problem;

  // Add variables to the objective function and constraint matrix
  for (int i = 0; i < _problem->get_num_cols(); i++) {
    // Add a new variable
    CoinPackedVector col;
    addCol(col, 0.0, 1.0, _problem->get_obj_coef(i));
    // Set variable type
    setInteger(i);
  }
  // Add constraints
  for (int i = 0; i < _problem->get_num_rows(); i++) {
    // Convert PackedVector to CoinPackedVector
    // TODO: do we have more efficient way to do this?
    PackedVector* source_row = _problem->get_row(i);
    CoinPackedVector target_row(source_row->get_num_elements(),
				source_row->get_indices(),
				source_row->get_elements());
    addRow(target_row, 'L', _problem->get_row_upper_bound(i), 1.0);
  }
  // Set problem sense
  setObjSense(_problem->get_obj_sense());
}
