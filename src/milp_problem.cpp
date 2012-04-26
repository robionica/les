/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <set>

#include <les/milp_problem.hpp>

const char* MILPP::OBJ_SENSE_TO_STRING[] = {"min", NULL, "max"};

/** Default constructor. */
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
  initialize(nr_cols, nr_rows);

  /* Assign vector of coefficients for objective function */
  assign_obj_coefs(c);
  assign_rows_lower_bounds((double*)calloc(get_num_cols(), sizeof(double)));
  assign_rows_upper_bounds(b);

  assign_rows_senses(s);

  /* Fill the constraint matrix */
  for (size_t i = 0; i < get_num_rows(); i++)
    for (size_t j = 0; j < get_num_cols(); j++)
      {
        double v = (A + i * get_num_cols())[j];
        if (!v) continue;
        cons_matrix_.set_coefficient(i, j, v);
        col_to_row_mapping_[j]->insert(i);
        row_to_col_mapping_[i]->insert(j);
      }
}

void
MILPP::set_initial_data()
{
  obj_sense_ = 1;
}

void
MILPP::initialize(int nr_cols, int nr_rows)
{
  cons_matrix_.resize(nr_rows, nr_cols);

  col_to_row_mapping_.resize(nr_cols);
  for (int i = 0; i < get_num_cols(); i++)
    {
      col_to_row_mapping_[i] = new set<int>();
    }
  row_to_col_mapping_.resize(nr_rows);
  for (int i = 0; i < get_num_rows(); i++)
    {
      row_to_col_mapping_[i] = new set<int>();
    }

  /* Compute problem parameters and set default values if required */
  obj_coefs_.resize(nr_cols);
  cols_lower_bounds_.resize(nr_cols);
  cols_upper_bounds_.resize(nr_cols);

  /* Allocate rows related variables */
  rows_lower_bounds_.resize(nr_rows);
  rows_upper_bounds_.resize(nr_rows);
  rows_senses_.resize(nr_rows);

  /* Initialize cols related arrays */
  for (int i = 0; i < get_num_cols(); i++)
    {
      set_col_lower_bound(i, 0.);
      set_col_upper_bound(i, 1.);
      set_obj_coef(i, 0.);
    }

  /* Initialize rows related arrays */
  for (int i = 0; i < get_num_rows(); i++)
    {
      set_row_lower_bound(i, 0.);
      /* The actual upper bound values will be assigned later. */
      set_row_upper_bound(i, 0.);
      /* Set default row sense */
      set_row_sense(i, ROW_SENSE_LOWER);
    }
}

void
MILPP::set_cons_matrix(const PackedMatrix* matrix)
{
  cons_matrix_ = *matrix;

  for (int i = 0; i < get_num_rows(); i++)
    {
      PackedVector* row = get_row(i);
      for (int j = 0; j < row->get_num_elements(); j++)
        {
          col_to_row_mapping_[ row->get_index_by_pos(j) ]->insert(i);
          row_to_col_mapping_[i]->insert( row->get_index_by_pos(j) );
        }
    }
}

void
MILPP::print()
{
  int i;
  int j;
  int offset;

  /* Print objective function sense and its coefficients */
  for (int i = 0; i < get_num_cols(); ++i)
    {
      if (i) printf(" + ");
      printf("%.1fx%d", get_obj_coef(i), i);
    }
  printf(" -> %s\n", obj_sense_to_string());
  /* Print constraints represented by rows */
  printf("subject to\n");
  for (i = 0; i < cons_matrix_.get_num_rows(); i++)
    {
      int t = 0; /* start from col zero */
      PackedVector* row = cons_matrix_.get_vector(i);
      printf("(%d) ", i);
      for (j = 0; j < row->get_num_elements(); j++)
        {
          if (j > 0)
            printf(" + ");
          //printf("[%d|%d]", row->get_index_by_pos(j), t);
          if ((offset = row->get_index_by_pos(j) - t) >= 1)
            {
              if (j > 0)
                offset -= 1;
              //printf("(%d)", offset);
              offset *= 5 + 3;
              for (int s = 0; s < offset; s++)
                printf(" ");
            }
          t = row->get_index_by_pos(j);

          printf("%.1fx%d", row->get_element_by_pos(j),
                 row->get_index_by_pos(j));
        }
      /* Print row sense */
      printf(" <= ");
      /* Print row upper bound */
      printf("%.1f", get_row_upper_bound(i));
      printf("\n");
    }

}
