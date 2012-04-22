/*
 * Copyright (c) 2012 Alexander Sviridenko
 */
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include <les/quasiblock_milp_problem.hpp>

using namespace std;

/**
 * Setup generator. Compute required values.
 */
void
QBMILPPGenerator::setup(int block_width, int block_height, int bridge_size,
                        bool fixed_block_width, bool fixed_block_height,
                        bool fixed_bridge_size)
{
  params.block_height = block_height ? block_height : DEFAULT_BLOCK_HEIGHT;
  params.bridge_size = bridge_size ? bridge_size : DEFAULT_BRIDGE_SIZE;

  /* Compute number of blocks */
  params.nr_blocks = problem.get_num_rows() / params.block_height;

  /* Compute max block width */
  params.block_width = block_width ? block_width
    : (problem.get_num_cols() / params.nr_blocks);

  params.fixed_block_width = fixed_block_width;
  params.fixed_block_height = fixed_block_height;
  params.fixed_bridge_size = fixed_bridge_size;
}

QBMILPPGenerator::QBMILPPGenerator(int nr_cols, int nr_rows,
                                   int block_width, int block_height,
                                   int bridge_size,
                                   bool fixed_block_width,
                                   bool fixed_block_height,
                                   bool fixed_bridge_size)
{
  problem.initialize(nr_cols, nr_rows);
  setup(block_width, block_height, bridge_size,
        fixed_block_width, fixed_block_height, fixed_bridge_size);
}

/**
 * Generate and return quasi-block MILP problem. Optionally return
 * list of blocks.
 */
QBMILPP*
QBMILPPGenerator::generate()
{
  /* Initialize random seed */
  srand(time(NULL));
  /* Generate objective function */
  for (int i = 0; i < problem.get_num_cols(); i++)
    {
      /* Randomly pick up coefficient for selected variable */
      problem.set_obj_coef(i, 1. + (double)(rand() % problem.get_num_cols()));
    }
  /* Generate blocks once by one */
  generate_blocks();

  return get_problem();
}

void
QBMILPPGenerator::generate_blocks()
{
  int i;
  int j;
  int row_index;
  int col_index;
  Block* last_block = NULL;
  Block* curr_block;

  int nr_blocks;
  int nr_left_indices;
  int nr_middle_indices;
  int nr_right_indices;

  /* Initialize random seed */
  srand(time(NULL));

  blocks.reserve(params.nr_blocks);

  col_index = 0;

  for (i = 0; i < params.nr_blocks; i++)
    {
      curr_block = new Block();

      /* Compute number of the left indices */
      curr_block->set_left_indices((last_block != NULL) ? last_block->get_right_indices() : NULL);
      nr_left_indices = (last_block != NULL) ? last_block->count_right_indices() : 0;

      /* Compute number of right indices */
      if ((i + 1) == params.nr_blocks)
        nr_right_indices = 0;
      else if (params.fixed_bridge_size)
        nr_right_indices = params.bridge_size;
      else
        nr_right_indices = 1 + rand() % params.bridge_size;

      /* Define number of the middle indices */
      nr_middle_indices = params.block_width - nr_right_indices;

      /* Reserve space for middle indices and write them */
      curr_block->get_middle_indices()->reserve(nr_middle_indices);

      for (j = nr_left_indices; j < nr_left_indices + nr_middle_indices; j++)
        {
          curr_block->get_middle_indices()->push_back(col_index + j);
        }

      /* Reserve space for right indices and write them */
      curr_block->get_right_indices()->reserve(nr_right_indices);
      for (j = nr_left_indices + nr_middle_indices;
           j < nr_left_indices + nr_middle_indices + nr_right_indices; j++)
        {
          curr_block->get_right_indices()->push_back(col_index + j);
        }

      /* Start working with each row for specific block */
      curr_block->get_row_indices()->reserve(params.block_height);
      for (j = 0; j < params.block_height; j++)
        {
          row_index = i * params.block_height + j; /* compute row's position */
          generate_constraint(curr_block, row_index, col_index);
          curr_block->get_row_indices()->push_back(row_index);
        }

      /* Save freshly created block */
      blocks[i] = curr_block;

      col_index += nr_left_indices + nr_middle_indices;
      last_block = curr_block;
    }
}

void
QBMILPPGenerator::generate_constraint(Block* block,
                                      int row_index, int first_col_index)
{
  int i;
  PackedVector* row;
  double coef;
  double bound;
  double coef_sum;
  double coef_range = 4.0; /* define range for coefficients of a single row */

  row = new PackedVector();

  /* Define left part */
  printf("%d: left %d\n", row_index, block->count_left_indices());
  for (i = 0; i < block->count_left_indices(); i++)
    {
      coef = 1.0 + (coef_range * rand() / (RAND_MAX + 1.));
      row->insert(first_col_index + i, coef);
      coef_sum += coef;
    }
  /* middle part */
  printf("%d: middle %d\n", row_index, block->count_middle_indices());
  for (i = block->count_left_indices();
       i < block->count_left_indices() + block->count_middle_indices(); i++)
    {
      coef = 1.0 + (coef_range * rand() / (RAND_MAX + 1.));
      row->insert(first_col_index + i, coef);
      coef_sum += coef;
    }
  /* Define right part */
  printf("%d: right %d\n", row_index, block->count_right_indices());
  for (i = block->count_left_indices() + block->count_middle_indices();
       i < block->count_left_indices() + block->count_middle_indices() +
         block->count_right_indices(); i++)
    {
      coef = 1.0 + (coef_range * rand() / (RAND_MAX + 1.));
      row->insert(first_col_index + i, coef);
      coef_sum += coef;
    }

  /* Compute upper bound and right-hand side*/
  bound = coef_sum / 2.3;
  problem.set_row_upper_bound(row_index, bound);

  //problem.assign_row(row_index, row);
}
