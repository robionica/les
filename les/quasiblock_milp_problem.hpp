// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied.  See the License for the specific language governing
// permissions and limitations under the License.

/**
 * @file quasiblock_milp_problem.hpp
 * @brief Quasi-block MILP problem

 The following code snippet shows how to use QBMILPPGenerator to
 generate quasi-block MILP problems.

 \code
 QBMILPPGenerator generator(9, 4, 3, 2);
 QBMILPP* problem = generator.generate();
 problem->print();
 \endcode

 */

#ifndef __LES_QBMILPP_HPP
#define __LES_QBMILPP_HPP

#include <les/milp_problem.hpp>
#include <les/packed_vector.hpp>
#include <les/decomposition.hpp>

// QBMILP stands for Quasi-Block MILP problem.
class QBMILPP : public MILPP
{
public:

  /* Default constractor */
  QBMILPP() : MILPP() {  }
  QBMILPP(int nr_cols, int nr_rows) : MILPP(nr_cols, nr_rows) {}
  QBMILPP(double* c, int nr_cols, double* A, int nr_rows, char* s, double* b) :
    MILPP(c, nr_cols, A, nr_rows, s, b) {}
};

typedef struct {
  int num_cols;
  int num_rows;
  int nr_blocks;
  int block_width;
  int block_height;
  int bridge_size;
  bool fixed_block_width;
  bool fixed_block_height;
  bool fixed_bridge_size;
} qbmilpp_generator_params_t;

// Quasi-block MILP problem generator for automitic problem generating.
class QBMILPPGenerator
{
public:
  static const int DEFAULT_BLOCK_HEIGHT = 2;
  static const int DEFAULT_BRIDGE_SIZE = 1;

  // Default constructor.
  QBMILPPGenerator(int num_cols, int num_rows,
                   int block_width, int block_height,
                   int bridge_size = 0,
                   bool fixed_block_width = true,
                   bool fixed_block_height = true,
                   bool fixed_bridge_size = true);

  QBMILPP* generate();

  // Return pointer to the result problem.
  QBMILPP* get_problem()
  {
    return &problem;
  }

private:
  void setup(int block_width, int block_height, int bridge_size,
             bool fixed_block_width, bool fixed_block_height,
             bool fixed_bridge_size);

  void generate_blocks();
  void generate_constraint(Block* block, int row_index, int first_col_index);
  qbmilpp_generator_params_t params;

  vector<Block*> blocks;

  // Target quasi-block MILP problem.
  QBMILPP problem;
};

#endif  // __LES_QBMILPP_HXX
