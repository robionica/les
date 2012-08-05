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

#ifndef __LES_DECOMPOSITION_DECOMPOSER_HPP
#define __LES_DECOMPOSITION_DECOMPOSER_HPP

#include <vector>

#include <les/problem.hpp>
#include <les/interaction_graph.hpp>
#include <les/packed_matrix.hpp>

using namespace std;

class Block;
class BlockSolution;

typedef struct {
  double obj_value;
  double* left_values;
  double* middle_values;
} block_solution_t;

class BlockSolution {
  map<int, block_solution_t>& get_solutions()
  {
    return solutions;
  }

  block_solution_t& get_solution(int i)
  {
    return solutions[i];
  }

private:
  map<int, block_solution_t> solutions;
};


// Decomposition block. Blocks can be combined in sequence, tree, etc.
class DecompositionBlock {
public:
  DecompositionBlock(Problem* problem=NULL) {
    problem_ = problem;
    left_part_ = new PackedMatrix();
    middle_part_ = new PackedMatrix();
    right_part_ = new PackedMatrix();
    mark_as_unsolved();
  }

  inline Problem* get_problem() const { return problem_; }
  inline void set_left_part(PackedMatrix* part) { left_part_ = part; }
  inline PackedMatrix* get_left_part() { return left_part_; }
  inline PackedMatrix* get_middle_part() { return middle_part_; }
  inline void set_right_part(PackedMatrix* part) { right_part_ = part; }
  inline PackedMatrix* get_right_part() { return right_part_; }

  inline bool is_solved() { return _is_solved; }
  inline void mark_as_solved() { _is_solved = true; }
  inline void mark_as_unsolved() { _is_solved = false; }

  set<int>* get_nonzero_rows() const;

  /**
   * Return set of non-zero cols.
   */
  set<int>* get_nonzero_cols() const;

  block_solution_t* new_solution(int right_mask)
  {
    block_solution_t* solution = (block_solution_t*)malloc(sizeof(block_solution_t));
    right_mask_to_solution_mapping_[right_mask] = solution;
    double* left_values = (double*)malloc(left_part_->get_num_nonzero_cols() * sizeof(double));
    double* middle_values = (double*)malloc(middle_part_->get_num_nonzero_cols() * sizeof(double));
    solution->left_values = left_values;
    solution->middle_values = middle_values;
  }

  block_solution_t* find_solution_by_right_mask(int mask)
  {
    map<int, block_solution_t*>::iterator it;
    it = right_mask_to_solution_mapping_.find(mask); 
    if (it != right_mask_to_solution_mapping_.end())
      return it->second;
    return NULL;
  }

private:
  bool _is_solved;
  Problem* problem_;
  map<int, block_solution_t*> right_mask_to_solution_mapping_;
  PackedMatrix* left_part_;
  PackedMatrix* middle_part_;
  PackedMatrix* right_part_;
};

class Block {
public:
  Block() {
    left_indices = NULL;
    middle_indices = NULL;
    right_indices = NULL;
    row_indices = NULL;

    middle_indices = new vector<int>();
    right_indices = new vector<int>();
    row_indices  = new vector<int>();
  }

  vector<int>* get_left_indices() { return left_indices; }
  void set_left_indices(vector<int>* indices) { left_indices = indices; }
  int get_left_index(int pos) { return left_indices->at(pos); }
  int count_left_indices() { return (!get_left_indices()) ? 0 : get_left_indices()->size(); }

  vector<int>* get_middle_indices() { return middle_indices; }
  int get_middle_index(int pos) { return middle_indices->at(pos); }
  void set_middle_index(int pos, int index) { middle_indices->at(pos) = index; }
  int count_middle_indices() { return (!get_middle_indices()) ? 0 : get_middle_indices()->size(); }

  vector<int>* get_right_indices() { return right_indices; }
  int get_right_index(int pos) { return right_indices->at(pos); }
  void set_right_index(int pos, int index) { right_indices->at(pos) = index; }
  int count_right_indices() { return (!get_right_indices()) ? 0 : get_right_indices()->size(); }

  vector<int>* get_row_indices() { return row_indices; }
  int get_row_index(int pos) { return row_indices->at(pos); }
  void set_row_index(int pos, int index) { row_indices->at(pos) = index; }

  map<int, block_solution_t>& get_solutions() { return solutions; }
  block_solution_t& get_solution(int i) { return solutions[i]; }

private:
  vector<int>* left_indices;
  vector<int>* middle_indices;
  vector<int>* right_indices;
  vector<int>* row_indices;
  map<int, block_solution_t> solutions;
};

vector<Block*>*
block_decomposition_by_articulation_points(InteractionGraph* g);

void blocktree_decomposition(MILPP* problem);

class Decomposer {
public:
  Decomposer() {
  }
};

#endif /* __LES_DECOMPOSITION_DECOMPOSER_HPP */
