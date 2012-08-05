//

void LeSolver::solve(vector<DecompositionBlock*>* blocks, bool use_relaxation)
{
  (use_relaxation) ? solve_with_relaxation(blocks) : solve(blocks);
}

void LeSolver::solve_block(DecompositionBlock* block)
{

}

void LeSolver::solve(vector<DecompositionBlock*>* blocks)
{
  vector<DecompositionBlock*>::iterator it;
  block_solution_t* solution = NULL;
  DecompositionBlock* block = NULL;
  vector<int>* middle_cols;
  vector<int>* left_cols;
  int right_mask;
  size_t i;

  // NOTE: maybe we also need to check all the blocks, so they all
  // have to be from the same problem?
  MILPP* p = (MILPP*)blocks->back()->get_problem();

  // Solve the blocks one by one
  BOOST_FOREACH(block, *blocks) {
    if (!block->is_solved()) {
      solve_block(block);
    }
  }

  // Initialize array of primal solution vector
  _obj_value = 0.0;
  solution_.clear();
  solution_.resize( p->get_num_cols() );

  // Initial right mask
  right_mask = 0;

#if 0
  BOOST_REVERSE_FOREACH(block, *blocks) {
    solution = block->find_solution_by_right_mask(right_mask);
    assert(solution != NULL);

    middle_cols = block->get_middle_part()->get_nonzero_cols();
    left_cols = block->get_left_part()->get_nonzero_cols();

    // fix block's obj value
    if (it != blocks->begin()) {
      DecompositionBlock* prev_block = *(it - 1);
      int left_mask = convert_bin_to_dec(solution->left_values, left_cols->size());
      block_solution_t* prev_solution = prev_block->find_solution_by_right_mask(left_mask);
      assert(prev_solution != NULL);
      solution->obj_value += prev_solution->obj_value;
    }

    for (i = 0; i < middle_cols->size(); i++) {
      assert(solution->middle_values != NULL);
      solution_[ middle_cols->at(i) ] = solution->middle_values[i];
      if (solution->middle_values[i]) {
        _obj_value += p->get_obj_coef( middle_cols->at(i) );
      }
    }
    for (i = 0; i < left_cols->size(); i++) {
      assert(solution->left_values != NULL);
      solution_[ left_cols->at(i) ] = solution->left_values[i];
      if (solution->left_values[i]) {
        _obj_value += p->get_obj_coef( left_cols->at(i) );
      }
    }
    if (left_cols->size()) {
      right_mask = convert_bin_to_dec(solution->left_values, left_cols->size());
    }
  }
#endif
}

void
OsiLeSolverInterface::solve_with_relaxation(vector<DecompositionBlock*>* blocks)
{
  vector<DecompositionBlock*>::iterator it;
  block_solution_t* solution = NULL;
  DecompositionBlock* block = NULL;
  vector<int>* middle_cols;
  vector<int>* left_cols;
  int right_mask;
  size_t i;

  /* NOTE: maybe we also need to check all the blocks, so they all
     have to be from the same problem?*/
  MILPP* p = (MILPP*)blocks->back()->get_problem();

  /* Solve the blocks one by one */
  BOOST_FOREACH(block, *blocks)
    {
      if (!block->is_solved())
        solve_block(block);
    }

  _obj_value = 0.0;

  /* Initialize array of primal solution vector */
  solution_.clear();
  solution_.resize( p->get_num_cols() );

  /* Initial right mask */
  right_mask = 0;

  for (it = blocks->end() - 1; it >= blocks->begin(); it--)
    {
      block = *it;

      solution = block->find_solution_by_right_mask(right_mask);
      assert(solution != NULL);

      middle_cols = block->get_middle_part()->get_nonzero_cols();
      left_cols = block->get_left_part()->get_nonzero_cols();

      /* fix block's obj value */
      if (it != blocks->begin())
        {
          DecompositionBlock* prev_block = *(it - 1);
          int left_mask = convert_bin_to_dec(solution->left_values, left_cols->size());
          block_solution_t* prev_solution = prev_block->find_solution_by_right_mask(left_mask);
          assert(prev_solution != NULL);
          solution->obj_value += prev_solution->obj_value;
        }

      for (i = 0; i < middle_cols->size(); i++)
        {
          assert(solution->middle_values != NULL);
          solution_[ middle_cols->at(i) ] = solution->middle_values[i];
          if (solution->middle_values[i])
            {
              _obj_value += p->get_obj_coef( middle_cols->at(i) );
            }
        }
      for (i = 0; i < left_cols->size(); i++)
        {
          assert(solution->left_values != NULL);
          solution_[ left_cols->at(i) ] = solution->left_values[i];
          if (solution->left_values[i])
            {
              _obj_value += p->get_obj_coef( left_cols->at(i) );
            }
        }
      if (left_cols->size())
        {
          right_mask = convert_bin_to_dec(solution->left_values, left_cols->size());
        }
    }
}
