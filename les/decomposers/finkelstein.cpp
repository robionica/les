/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied.  See the License for the specific language governing
 * permissions and limitations under the License.
 */

#include <boost/foreach.hpp>

#include "finkelstein.hpp"

void
FinkelsteinQBDecomposition::dump()
{
  for (size_t i = 0; i < _U.size(); i++) {
    std::cout << " U" << i << " : {";
    BOOST_FOREACH(int row, _U[i]) {
      std::cout << row << ", ";
    }
    std::cout << "}" << std::endl;
  }

  for (size_t i = 0; i < _S.size(); i++) {
    std::cout << " S" << i << " : {";
    BOOST_FOREACH(int col, _S[i]) {
      std::cout << col << ", ";
    }
    std::cout << "}" << std::endl;
  }

  for (size_t i = 0; i < _M.size(); i++) {
    std::cout << " M" << i << " : {";
    BOOST_FOREACH(int col, _M[i]) {
      std::cout << col << ", ";
    }
    std::cout << "}" << std::endl;
  }
}

vector<QBMILPP*>
FinkelsteinQBDecomposition::get_subproblems()
{
  vector<QBMILPP*> subproblems;
  /* Decompose a problem by using finkelstein algorithm */
  decompose(_problem);
  for (size_t i = 0; i < _U.size(); i++) {
    int nr_cols = ((i > 0) ? _S[i - 1].size() : 0) + _M[i].size()
      + (((_U.size() - i) > 1) ? _S[i].size() : 0);
    int nr_rows = _U[i].size();
    QBMILPP* subproblem = new QBMILPP(nr_cols , nr_rows);
    PackedMatrix* cons = subproblem->get_cons_matrix();
    // Define objective function for the subproblem.
    // XXX: Take the index of the first variable from M.
    int first_v = (!i) ? *(_M[i].begin()) : *(_S[i-1].begin());
    for (int j = first_v; j < (first_v + nr_cols); j++) {
      subproblem->set_obj_coef(j, _problem->get_obj_coef(j));
    }
    /* For each constraint... */
    BOOST_FOREACH(int u, _U[i]) {
      PackedVector* row = _problem->get_row(u);
      if (i > 0) {
        BOOST_FOREACH(int s, _S[i - 1]) {
          if (row->get_element_by_index(s) != 0.0) {
            cons->set_coefficient(u, s, row->get_element_by_index(s));
          }
        }
      }
      BOOST_FOREACH(int m, _M[i]) {
        if (row->get_element_by_index(m) != 0.0) {
          cons->set_coefficient(u, m, row->get_element_by_index(m));
        }
      }
      if ((_U.size() - i) > 1) {
        BOOST_FOREACH(int s, _S[i]) {
          if (row->get_element_by_index(s) != 0.0) {
            cons->set_coefficient(u, s, row->get_element_by_index(s));
          }
        }
      }
      subproblem->set_row_upper_bound(u, _problem->get_row_upper_bound(u));
    }
    subproblems.push_back(subproblem);
  }

  return subproblems;
}

vector<DecompositionBlock*>*
FinkelsteinQBDecomposition::decompose_by_blocks(MILPP* problem)
{
  PackedMatrix* left_part;
  PackedMatrix* middle_part;
  PackedMatrix* right_part;
  DecompositionBlock* next_block;
  DecompositionBlock* prev_block;
  vector<DecompositionBlock*>* blocks;

  blocks = new vector<DecompositionBlock*>();
  next_block = prev_block = NULL;

  /* Decompose a problem by using finkelstein algorithm */
  decompose(problem);

  for (size_t i = 0; i < _U.size(); i++) {
    next_block = new DecompositionBlock(problem);
    left_part = next_block->get_left_part();
    middle_part = next_block->get_middle_part();
    right_part = next_block->get_right_part();
    /* for each constraint */
    for (set<int>::iterator u = _U[i].begin(); u != _U[i].end(); u++) {
      PackedVector* row = problem->get_row(*u);
      if (i > 0) {
        for (set<int>::iterator s = _S[i-1].begin(); s != _S[i-1].end(); s++) {
          if (row->get_element_by_index(*s) != 0.0) {
            left_part->set_coefficient(*u, *s, row->get_element_by_index(*s));
          }
        }
      }
      for (set<int>::iterator m = _M[i].begin(); m != _M[i].end(); m++) {
        if (row->get_element_by_index(*m) != 0.0) {
          middle_part->set_coefficient(*u, *m, row->get_element_by_index(*m));
        }
        if ((_U.size() - i) > 1) {
          for (set<int>::iterator s = _S[i].begin(); s != _S[i].end(); s++) {
            if (row->get_element_by_index(*s) != 0.0) {
              right_part->set_coefficient(*u, *s, row->get_element_by_index(*s));
            }
          }
        }
      }
      if (prev_block) {
        //next_block->set_left_part(prev_block->get_right_part());
      }
      blocks->push_back(next_block);
      prev_block = next_block;
    }
  return blocks;
  }

// TODO: On this moment it returns nothing. Maybe we need some error status?
void
FinkelsteinQBDecomposition::decompose(MILPP* problem, vector<int>* initial_cols,
                                      int max_separator_size,
                                      bool merge_empty_blocks)
{
  if (problem) {
    _problem = problem;
  }
  assert(problem != NULL);

  vector< set<int> > S_; // S'
  vector< set<int> > U_; // U'

  _U.clear();
  _S.clear();
  _M.clear();

  set<int> cols_diff;
  set<int> prev_cols;
  set<int> rows;

  // If initial columns was not provided use default columns.
  if (initial_cols == NULL) {
    // Let us start from column 0.
    initial_cols = new vector<int>(1, 0);
  }

  // The first iteration will be implemented out of loop to avoid unnecessary
  // if-statements.
  set<int> cols = set<int>(initial_cols->begin(), initial_cols->end());

  while (1) {
    cols_diff.clear();
    rows = *_problem->get_rows_related_to_cols(&cols);
    assert(!rows.empty());

    prev_cols = cols;
    cols = *_problem->get_cols_related_to_rows(&rows);

    set_difference(cols.begin(), cols.end(),
                   prev_cols.begin(), prev_cols.end(),
                   inserter(cols_diff, cols_diff.begin()));

    // Store the new set of columns and rows. We also need to store the last
    // set even it will be empty. In some cases there might be exception such
    // as blocks of right-separators.
    S_.push_back(cols);
    U_.push_back(rows);

    if (cols_diff.empty()) {
      break;
    }
  }

  rows = U_.at(0);
  _U.push_back(rows);

  for (vector< set<int> >::iterator it = U_.begin() + 1; it != U_.end(); it++) {
    set<int> u_diff = set<int>();
    set_difference((*it).begin(), (*it).end(), rows.begin(), rows.end(),
                   inserter(u_diff, u_diff.begin()));
    _U.push_back(u_diff);
    rows = *it;
  }

  // Find all separators, where the separator is left/right part of a block.
  for (vector< set<int> >::iterator it = _U.begin(); it != _U.end() - 1; it++) {
    set<int> s = set<int>(); /* separator */
    set<int>& rows = *(it + 1);
    cols = *_problem->get_cols_related_to_rows(&rows);
    set<int>& prev_rows = *it;
    prev_cols = *_problem->get_cols_related_to_rows(&prev_rows);
    set_intersection(cols.begin(), cols.end(),
                     prev_cols.begin(), prev_cols.end(),
                     inserter(s, s.begin()));
    if (max_separator_size && s.size() > max_separator_size) {
      prev_rows.insert(rows.begin(), rows.end());
      _U.erase(it + 1);
      it--;
      continue;
    }
    _S.push_back(s);
  }

  // Find middle part for each block if required
  cols = *_problem->get_cols_related_to_rows(&_U[0]);
  cols_diff.clear();

  set_difference(cols.begin(), cols.end(),
                 _S[0].begin(), _S[0].end(),
                 inserter(cols_diff, cols_diff.begin()));
  _M.push_back(cols_diff);

  vector<int> e = vector<int>();

  for (size_t i = 1; i < (_U.size() - 1); i++) {
    set<int> sep_union;

    cols_diff.clear();

    set_union(_S[i - 1].begin(), _S[i - 1].end(),
              _S[i].begin(), _S[i].end(),
              inserter(sep_union, sep_union.begin()));

    cols = *_problem->get_cols_related_to_rows(&_U[i]);
    set_difference(cols.begin(), cols.end(),
                   sep_union.begin(), sep_union.end(),
                   inserter(cols_diff, cols_diff.begin()));
    _M.push_back(cols_diff);
  }

  cols = *_problem->get_cols_related_to_rows(&(*(_U.end() - 1)));
  cols_diff.clear();
  set_difference(cols.begin(), cols.end(),
                 (*(_S.end() - 1)).begin(), (*(_S.end() - 1)).end(),
                 inserter(cols_diff, cols_diff.begin()));
  _M.push_back(cols_diff);

  if (merge_empty_blocks) {
    for (size_t i = 1; i < _U.size(); i++) {
      if (!_M[i].empty()) {
        continue;
      }
      _U[i - 1].insert( _U[i].begin(), _U[i].end() );
      _M[i - 1].insert( _S[i - 1].begin(), _S[i - 1].end() );

      _U.erase(_U.begin() + i);
      _M.erase(_M.begin() + i);
      _S.erase(_S.begin() + i - 1);

      i--;
    }
  }

  // DEBUG
  assert(_U.size() == _M.size());
  assert(_U.size() == (_S.size() + 1));
#if 1
  int num_rows = 0;
  for (vector< set<int> >::iterator it = _U.begin(); it != _U.end(); it++)
    num_rows += (*it).size();
  int num_cols = 0;
  for (vector< set<int> >::iterator it = _S.begin(); it != _S.end(); it++)
    num_cols += (*it).size();
  for (vector< set<int> >::iterator it = _M.begin(); it != _M.end(); it++)
    num_cols += (*it).size();
  //assert(_problem->get_num_rows() == num_rows);
  //assert(_problem->get_num_cols() == num_cols);
#endif
}
