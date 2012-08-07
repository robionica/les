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
//
// Mixed Integer Linear Programming (MILP) problem.

#ifndef __LES_MILPP_H
#define __LES_MILPP_H

#include <vector>
#include <set>
#include <assert.h>

#include <les/problem.hpp>
#include <les/packed_matrix.hpp>
#include <les/graph.hpp>

using namespace std;

// This class represents Mixed-Integer Linear Programming Problem (MILPP).
class MILPP : public Problem
{
public:
  static const int ROW_SENSE_LOWER   = 'L'; // <=
  static const int ROW_SENSE_EQUAL   = 'E'; // =
  static const int ROW_SENSE_GREATER = 'G'; // >=

  static const char OBJ_SENSE_MINIMISATION = +1;
  static const char OBJ_SENSE_MAXIMISATION = -1;

  static const char* OBJ_SENSE_TO_STRING[];

  // Constructors.
  MILPP();
  MILPP(int nr_cols, int nr_rows);
  MILPP(double* c, int nr_cols, double* A, int nr_rows, char* s, double* b);

  void initialize(int nr_cols, int nr_rows);
  void initialize(double* c, int nr_cols, double* A, int nr_rows, char* s,
                  double* b);

  // Print the problem, so we humans can analyse it.
  void dump();

  // Get number of columns.
  inline int get_num_cols() {
    return cons_matrix_.get_num_cols();
  }

  // This method will provide memory allocation for all variables that related
  // to number of cols.
  // WARNING: this may provide crash. Not safe.
  inline void set_num_cols(size_t n) {
    assert(n > 0);
    // Do not restructure problem if number of cols wasn't changed
    if (get_num_cols() == n) {
      return;
    }
    // Do restructuring
    cons_matrix_.resize(get_num_rows(), n);
    // Compute problem parameters and set default values if required
    _obj_coefs.resize(n);
    cols_lower_bounds_.resize(n);
    cols_upper_bounds_.resize(n);

    col_to_row_mapping_.resize(n);
    for (int i = 0; i < get_num_cols(); i++) {
      col_to_row_mapping_[i] = new set<int>();
    }
    // Initialize cols related arrays
    for (int i = 0; i < n; i++) {
      set_col_lower_bound(i, 0.0);
      set_col_upper_bound(i, 1.0);
      set_obj_coef(i, 0.);
    }
  }

  // Set a single column lower bound.
  inline void set_col_lower_bound(int i, double v) {
    assert(i < get_num_cols());
    cols_lower_bounds_[i] = v;
  }

  // Get col lower bound.
  inline double get_col_lower_bound(int i) {
    assert(i < get_num_cols());
    return cols_lower_bounds_[i];
  }

  // Set a single column upper bound.
  inline void set_col_upper_bound(int i, double v) {
    assert(i < get_num_cols());
    cols_upper_bounds_[i] = v;
  }

  inline double get_col_upper_bound(int i) {
    assert(i < get_num_cols());
    return cols_upper_bounds_[i];
  }

  inline PackedMatrix* get_cons_matrix() {
    return &cons_matrix_;
  }

  inline void set_num_rows(size_t n) {
    assert(n > 0);
    // Do not restructure problem if number of rows wasn't changed
    if (get_num_rows() == n) {
      return;
    }

    row_to_col_mapping_.resize(n);
    for (int i = 0; i < n; i++) {
      row_to_col_mapping_[i] = new set<int>();
    }

    // Allocate rows related variables
    _rows_lower_bounds.resize(n);
    _rows_upper_bounds.resize(n);
    _rows_senses.resize(n);

    cons_matrix_.resize(n, get_num_cols());

    // Initialize rows related arrays
    for (int i = 0; i < n; i++) {
      set_row_lower_bound(i, 0.0);
      // The actual upper bound values will be assigned later.
      set_row_upper_bound(i, 0.0);
      // Set default row sense
      set_row_sense(i, ROW_SENSE_LOWER);
    }
  }

  // Set constraint matrix where the matrix is represented by an arrays.
  void set_cons_matrix(double* A, int nr_rows, int nr_cols);

  // Set constraint matrix.
  void set_cons_matrix(const PackedMatrix* matrix);

  inline const set<int>* get_rows_related_to_col(int i) {
    return col_to_row_mapping_[i];
  }

  inline set<int>* get_rows_related_to_cols(set<int>* s) {
    set<int>* u = new set<int>(); // new set of rows
    for (set<int>::iterator it = s->begin(); it != s->end(); it++) {
      const set<int>* rows = get_rows_related_to_col(*it);
      u->insert(rows->begin(), rows->end());
    }
    return u;
  }

  inline const set<int>* get_cols_related_to_row(int i) {
    return row_to_col_mapping_[i];
  }

  inline set<int>* get_cols_related_to_rows(set<int>* u) {
    set<int>* s = new set<int>();
    for (set<int>::iterator it = u->begin(); it != u->end(); it++) {
      const set<int>* cols = get_cols_related_to_row(*it);
      s->insert(cols->begin(), cols->end());
    }
    return s;
  }

  inline PackedVector* get_first_row() {
    return get_row(0);
  }

  inline PackedVector* get_row(int i) {
    return cons_matrix_.get_vector(i);
  }

  inline int get_num_rows() {
    return cons_matrix_.get_num_rows();
  }

  inline double get_row_lower_bound(int i) {
    assert(i < get_num_rows());
    return _rows_lower_bounds.get_element_by_index(i);
  }

  inline void set_row_lower_bound(int i, double v) {
    assert(i < get_num_rows());
    _rows_lower_bounds.set_element_by_index(i, v);
  }

  // Set lower bound for each row
  inline void set_rows_lower_bounds(double* b) {
    for (size_t i = 0; i < get_num_rows(); i++) {
      set_row_lower_bound(i, b[i]);
    }
  }

  inline double get_row_upper_bound(int i) {
    assert(i < get_num_rows());
    return _rows_upper_bounds.get_element_by_index(i);
  }

  inline void set_row_upper_bound(int i, double v) {
    assert(i < get_num_rows());
    _rows_upper_bounds.set_element_by_index(i, v);
  }

  inline void set_rows_upper_bounds(double* b) {
    for (int i = 0; i < get_num_rows(); i++) {
      set_row_upper_bound(i, b[i]);
    }
  }

  inline void set_row_sense(int i, char s) {
    assert(i < get_num_rows());
    _rows_senses.set_element_by_index(i, s);
  }

  inline void set_rows_senses(char* s) {
    for (size_t i = 0; i < get_num_rows(); i++) {
      set_row_sense(i, s[i]);
    }
  }
  inline char get_row_sense(int i) {
    assert(i < get_num_rows());
    return _rows_senses.get_element_by_index(i);
  }

  inline double get_row_rhs(int i) {
    assert(i < get_num_rows());
    return _rows_upper_bounds.get_element_by_index(i);
  }

  // Get the objective function sense (OBJ_SENSE_MINIMISATION for minimisation
  // (default), OBJ_SENSE_MAXIMISATION for maximisation).
  inline const char* obj_sense_to_string() {
    return OBJ_SENSE_TO_STRING[(int)get_obj_sense() + 1];
  }

  inline void set_obj_sense(double sense) {
    obj_sense_ = sense;
  }

  inline double get_obj_sense() {
    return obj_sense_;
  }

  // Get pointer to array of objective function coefficients. Return 0.0 if
  // coefficient with such index doesn't exist.
  inline double get_obj_coef(int i) {
    if (i >= get_num_cols()) {
      return 0.0;
    }
    // TODO: do we need to do assert if number of cols greater than number of
    // obj coefs?
    return _obj_coefs.get_element_by_index(i);
  }

  // Assign new coefficients for the objective function. Note, the
  // size of an array must be get_num_cols().
  inline void set_obj_coefs(double* c) {
    assert(get_num_cols() > 0);
    for (int i = 0; i < get_num_cols(); i++) {
      set_obj_coef(i, c[i]);
    }
  }

  inline void set_obj_coefs(double* c, size_t n) {
    set_num_cols(n);
    set_obj_coefs(c);
  }

  // Set coefficient for a single column.
  inline void set_obj_coef(int i, double v) {
    _obj_coefs.set_element_by_index(i, v);
  }

private:
  // Set object state for default constructor.
  //
  // This routine establishes the initial values of data fields in the
  // object when the object is created using the default constructor.
  void set_initial_data();

  PackedVector _obj_coefs; // vector of objective coefficients.
  char obj_sense_;

  vector<double> cols_lower_bounds_;
  vector<double> cols_upper_bounds_;

  PackedVector _rows_lower_bounds;
  PackedVector _rows_upper_bounds;
  // Vector where each element represents sense of corresponding row.
  PackedVector _rows_senses;

  vector<set<int>*> col_to_row_mapping_;
  vector<set<int>*> row_to_col_mapping_;

  // Constraint matrix
  PackedMatrix cons_matrix_;
};

#endif // __LEP_MILPP_HPP
