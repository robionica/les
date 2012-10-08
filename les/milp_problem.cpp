/*
 * Implements milp_problem.hpp interface.
 *
 * Copyright (c) 2012 Oleksander Sviridenko
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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <set>

#include "les/milp_problem.hpp"

const char* MILPP::OBJ_SENSE_TO_STRING[] = {"max", NULL, "min"};

MILPP::MILPP()
{
  set_initial_data();
}

MILPP::MILPP(int nr_cols, int nr_rows)
{
  set_initial_data();
  initialize(nr_cols, nr_rows);
}

MILPP::MILPP(double* c, int nr_cols, double* A, int nr_rows,
             char* s, double* b)
{
  set_initial_data();
  initialize(c, nr_cols, A, nr_rows, s, b);
}

void MILPP::initialize(int nr_cols, int nr_rows)
{
  set_num_cols(nr_cols);
  set_num_rows(nr_rows);
}

void MILPP::initialize(double* c, int nr_cols, double* A, int nr_rows,
                       char* s, double* b)
{
  initialize(nr_cols, nr_rows);
  /* Set vector of coefficients for objective function */
  set_obj_coefs(c);
  set_rows_lower_bounds((double*)calloc(get_num_cols(), sizeof(double)));
  set_rows_upper_bounds(b);
  set_rows_senses(s);
  /* Set constraint matrix */
  set_cons_matrix(A, nr_rows, nr_cols);
}

void MILPP::set_cons_matrix(double* A, int nr_rows, int nr_cols)
{
  initialize(nr_cols, nr_rows);
  /* Fill the constraint matrix  */
  for (size_t i = 0; i < get_num_rows(); i++) {
    for (size_t j = 0; j < get_num_cols(); j++) {
      double v = (A + i * get_num_cols())[j];
      if (!v) continue;
      cons_matrix_.set_coefficient(i, j, v);
      col_to_row_mapping_[j]->insert(i);
      row_to_col_mapping_[i]->insert(j);
    }
  }
  set_rows_lower_bounds((double*)calloc(get_num_cols(), sizeof(double)));
}

void MILPP::set_initial_data()
{
  obj_sense_ = MILPP::OBJ_SENSE_MINIMISATION;
}

void MILPP::set_cons_matrix(const PackedMatrix* matrix)
{
  cons_matrix_ = *matrix;

  for (int i = 0; i < get_num_rows(); i++) {
    PackedVector* row = get_row(i);
    for (int j = 0; j < row->get_num_elements(); j++) {
      col_to_row_mapping_[ row->get_index_by_pos(j) ]->insert(i);
      row_to_col_mapping_[i]->insert( row->get_index_by_pos(j) );
    }
  }
}

void MILPP::dump()
{
  int i;
  int j;
  int offset;
  // Print objective function sense and its coefficients
  for (i = 0; i < get_num_cols(); i++) {
    if (get_obj_coef(i) == 0.0) {
      continue;
    }
    printf("%.1fx%d", get_obj_coef(i), i);
    break;
  }
  for (i = i + 1; i < get_num_cols(); i++) {
    if (get_obj_coef(i) == 0.0) {
      continue;
    }
    printf(" + %.1fx%d", get_obj_coef(i), i);
  }

  printf(" -> %s\n", obj_sense_to_string());
  // Print constraints represented by rows
  printf("subject to\n");
  for (i = 0; i < get_num_rows(); i++) {
    int t = 0; // start from col zero
    PackedVector* row = get_row(i);
    if (!row->size()) {
      continue;
    }
    printf("(%d) ", i);
    for (j = 0; j < row->get_num_elements(); j++) {
      if (j > 0) {
        printf(" + ");
      }
      if ((offset = row->get_index_by_pos(j) - t) >= 1) {
        if (j > 0) {
          offset -= 1;
        }
        offset *= 5 + 3;
        for (int s = 0; s < offset; s++)
          printf(" ");
      }
      t = row->get_index_by_pos(j);

      printf("%.1fx%d", row->get_element_by_pos(j), row->get_index_by_pos(j));
    }
    // Print row sense
    printf(" <= ");
    // Print row upper bound
    printf("%.1f", get_row_upper_bound(i));
    printf("\n");
  }
}
