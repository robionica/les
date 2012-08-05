// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <iostream>
#include <cstdlib>

//#include <boost/dynamic_bitset.hpp>
#include <boost/foreach.hpp>

#include <les/config.hpp>
#include <les/milp_problem.hpp>
#include <les/decomposition.hpp>
#include <les/packed_matrix.hpp>
#include <les/packed_vector.hpp>
#include <les/utils/math.hpp>

/* Include Coin-required API */
#include <coin/CoinPackedVector.hpp>

#include <les/bsolvers/symphony.hpp>

using namespace std;

double
OsiLeSolverInterface::get_obj_value()
{
  return _obj_value;
}

void
OsiLeSolverInterface::solve(vector<DecompositionBlock*>* blocks,
                            bool use_relaxation)
{
  if (use_relaxation)
    {
      solve_with_relaxation(blocks);
      return;
    }
  solve(blocks);
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

void
OsiLeSolverInterface::solve(vector<DecompositionBlock*>* blocks)
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

void
OsiLeSolverInterface::solve_block(DecompositionBlock* block)
{
  int i;
  block_solution_t* solution = NULL;
  double obj_value;

  assert(block != NULL);

  MILPP* p = (MILPP*)block->get_problem();

  int right_mask;
  int left_mask;

  PackedMatrix* right_matrix;
  PackedMatrix* middle_matrix;
  PackedMatrix* left_matrix;

  vector<int>* right_cols;
  vector<int>* middle_cols;
  vector<int>* left_cols;

  PackedVector left; /* vector of left assignments */

  /* Setup solver for intermediate calculations */
  OsiSymSolverInterface si;
  si.setSymParam("generate_cgl_cuts", FALSE);
  si.setSymParam(OsiSymVerbosity, -2);

  right_matrix = block->get_right_part();
  middle_matrix = block->get_middle_part();
  left_matrix = block->get_left_part();

  /* Get cols that will be presented in objective function. */
  right_cols = right_matrix->get_nonzero_cols();
  middle_cols = middle_matrix->get_nonzero_cols();
  left_cols = left_matrix->get_nonzero_cols();

  left.init(*left_cols);

  /* Start to generate objective function which is based on middle
     matrix. */
  for (i = 0; i < middle_cols->size(); i++)
    {
      CoinPackedVector col;
      int v = middle_cols->at(i);
      double c = p->get_obj_coef(v);
      /* Add column and its bounds from the main problem */
      si.addCol(col, p->get_col_lower_bound(v), p->get_col_upper_bound(v), c);
      si.setObjCoeff(i, c);
    }

  assert(si.getNumCols() > 0);

  /* Set column type. At some point we can not set column type when there
     is only one column in the problem. Otherwise SYMPHONY crashes
     with segmentation fault.*/

  if (si.getNumCols() > 1)
    {
      for (i = 0; i < middle_cols->size(); i++)
        si.setInteger(i);
    }

  set<int>* cons = block->get_nonzero_rows();
  vector<int>* middle_cons = middle_matrix->get_nonzero_rows();

  /* Start to generate rows */
  BOOST_FOREACH(int con, *middle_cons)
    {
      CoinPackedVector dst_row;
      PackedVector* src_row = middle_matrix->get_row(con);
      for (int j = 0; j < src_row->get_num_elements(); j++)
        dst_row.insert(j, src_row->get_element_by_pos(j));
      si.addRow(dst_row, p->get_row_sense(con),
                p->get_row_upper_bound(con), 1.0);
      delete src_row;
    }

  // TODO
  //boost::dynamic_bitset<> right_mask( right_cols->size() ); /* all zero by default */
  //boost::dynamic_bitset<> final_right_mask();
  //const boost::dynamic_bitset<> b1(2, 1);

  /* Fix mask of right assignments */
  for (right_mask = 0; right_mask < (1 << right_cols->size()); right_mask += 1)
    /* Once the right mask for right assignment was defined we will
       generate left assignment */
    for (left_mask = 0; left_mask < (1 << left.size()); left_mask += 1)
      {
        set<int>::iterator con;

        /* Zero all left values and start identify them by mask  */
        left.zero();

        for (i = 0, con = cons->begin(); con != cons->end(); con++, i++)
          {
            double rhs = abs(p->get_row_rhs(*con));
            for (int j = 0; j < left.size(); j++)
              if (left_mask & (1 << j))
                {
                  rhs -= left_matrix->get_coef(*con, left.get_index(j));
                  left.set_element(j, 1.0);
                }

            for (int j = 0; j < right_cols->size(); j++)
              {
                if (right_mask & (1 << j))
                  rhs -= right_matrix->get_coef(*con, right_cols->at(j));
              }
            si.setRowUpper(i, rhs);
          }

        // The new objective function has the same sense that main objective.
        // NOTE: can not set objective sense once at the bottom since, solver
        // modifies coefficients.
        si.setObjSense( p->get_obj_sense() );

        // HERE is a point where the problem will be solved by slave solver.
        si.branchAndBound();

        /* Obtain objective value and fix it.
           Revise using of abs(). */
        obj_value = abs(si.getObjValue());
        for (i = 0; i < left.size(); i++)
          {
            if (left.get_element(i))
              obj_value += abs(p->get_obj_coef( left.get_index(i) ));
          }

        solution = block->find_solution_by_right_mask(right_mask);

        // If solution already exists and its objective value greater
        // then the new once that it should be omitted.
        if (solution != NULL && solution->obj_value > obj_value)
          continue;

        /* Update solution, since a new or better solution for the
           same right assignment has been found. */
        if (solution == NULL)
            solution = block->new_solution(right_mask);
        solution->obj_value = obj_value;
        /* Copy new left assignment */
        memcpy(solution->left_values, left.get_elements(),
               left.size() * sizeof(double));
        /* Copy new middle assignment */
        memcpy(solution->middle_values, si.getColSolution(),
               si.getNumCols() * sizeof(double));

#if 0
        for (i = 0; i < si.getNumCols(); i++)
          printf("x%d=%0.1f, ", middle_cols->at(i), si.getColSolution()[i]);
        printf("Obj value = %f\n", obj_value);
#endif
      }

  /* Block has been solved */
  block->mark_as_solved();
}
