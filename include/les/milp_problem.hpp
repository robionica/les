/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file milp_problem.hpp
 * @brief Mixed Integer Linear Programming (MILP) problem.
 */

#ifndef __MILPP_H
#define __MILPP_H

#include <vector>
#include <set>
#include <assert.h>

#include <les/problem.hpp>
#include <les/packed_matrix.hpp>

using namespace std;

class MILPP;

class MILPP : public Problem
{
public:
  static const int ROW_SENSE_LOWER   = 'L'; /* <= */
  static const int ROW_SENSE_EQUAL   = 'E'; /* = */
  static const int ROW_SENSE_GREATER = 'G'; /* >= */

  static const char OBJ_SENSE_MINIMISATION = +1;
  static const char OBJ_SENSE_MAXIMISATION = -1;

  static const char* OBJ_SENSE_TO_STRING[];

  MILPP();
  MILPP(int nr_cols, int nr_rows);
  MILPP(double* c, int nr_cols, double* A, int nr_rows, char* s, double* b);

  void initialize(int nr_cols, int nr_rows);
  /** Print the problem, so we humans can analyse it. */
  void print();

  // -----------------------------------------------------------------
  /** @name Columns */
  /** @{ */

  /** Get number of columns */
  inline int get_num_cols()
  {
    return cons_matrix_.get_num_cols();
  }
  /** Set a single column lower bound. */
  inline void set_col_lower_bound(int i, double v)
  {
    assert(i < get_num_cols());
    cols_lower_bounds_[i] = v;
  }
  /** Get col lower bound. */
  inline double get_col_lower_bound(int i)
  {
    assert(i < get_num_cols());
    return cols_lower_bounds_[i];
  }
  /** Set a single column upper bound. */
  inline void set_col_upper_bound(int i, double v)
  {
    assert(i < get_num_cols());
    cols_upper_bounds_[i] = v;
  }
  inline double get_col_upper_bound(int i)
  {
    return cols_upper_bounds_[i];
  }

  /** @} */

  /** @name Rows */
  /** @{ */

  inline const PackedMatrix* get_cons_matrix()
  {
    return &cons_matrix_;
  }

  inline const set<int>* get_rows_related_to_col(int i)
  {
    return col_to_row_mapping_[i];
  }

  inline set<int>*
  get_rows_related_to_cols(set<int>* s)
  {
    set<int>* u = new set<int>(); /* new set of rows */
    for (set<int>::iterator it = s->begin(); it != s->end(); it++)
      {
        const set<int>* rows = get_rows_related_to_col(*it);
        u->insert(rows->begin(), rows->end());
      }
    return u;
  }

  inline const set<int>* get_cols_related_to_row(int i)
  {
    return row_to_col_mapping_[i];
  }

  inline set<int>*
  get_cols_related_to_rows(set<int>* u)
  {
    set<int>* s = new set<int>();
    for (set<int>::iterator it = u->begin(); it != u->end(); it++)
      {
        const set<int>* cols = get_cols_related_to_row(*it);
        s->insert(cols->begin(), cols->end());
      }
    return s;
  }

  inline PackedVector* get_row(int i)
  {
    return cons_matrix_.get_vector(i);
  }

  inline int get_num_rows() { return cons_matrix_.get_num_rows(); }
  inline double get_row_lower_bound(int i)
  {
    assert(i < get_num_rows());
    return rows_lower_bounds_[i];
  }
  inline void set_row_lower_bound(int i, double v)
  {
    assert(i < get_num_rows());
    rows_lower_bounds_[i] = v;
  }
  inline void assign_rows_lower_bounds(double* b)
  {
    for (size_t i = 0; i < get_num_rows(); i++)
      set_row_lower_bound(i, b[i]);
  }

  inline double get_row_upper_bound(int i)
  {
    assert(i < get_num_rows());
    return rows_upper_bounds_[i];
  }
  inline void set_row_upper_bound(int i, double v)
  {
    assert(i < get_num_rows());
    rows_upper_bounds_[i] = v;
  }
  inline void assign_rows_upper_bounds(double* b)
  {
    for (int i = 0; i < get_num_rows(); i++)
      set_row_upper_bound(i, b[i]);
  }

  inline void set_row_sense(int i, char s)
  {
    assert(i < get_num_rows());
    rows_senses_[i] = s;
  }
  inline void assign_rows_senses(char* s)
  {
    for (size_t i = 0; i < get_num_rows(); i++)
      set_row_sense(i, s[i]);
  }
  inline char get_row_sense(int i)
  {
    assert(i < get_num_rows());
    return rows_senses_[i];
  }
  inline double get_row_rhs(int i)
  {
    assert(i < get_num_rows());
    return rows_upper_bounds_[i];
  }

  /** @} */

  /** @name Objective function */
  /** @{ */

  /**
   * Get the objective function sense (OBJ_SENSE_MINIMISATION for
   * minimisation (default), OBJ_SENSE_MAXIMISATION for
   * maximisation).
   */
  inline const char* obj_sense_to_string()
  {
    return OBJ_SENSE_TO_STRING[(int)get_obj_sense() + 1];
  }
  inline void set_obj_sense(double sense)
  {
    obj_sense_ = sense;
  }
  inline double get_obj_sense()
  {
    return obj_sense_;
  }
  /** Get pointer to array of objective function coefficients */
  inline double get_obj_coef(int i)
  {
    return obj_coefs_[i];
  }
  /**
   * Assign new coefficients for the objective function. Note, the
   * size of an array must be get_num_cols().
   */
  inline void assign_obj_coefs(double* c)
  {
    for (int i = 0; i < get_num_cols(); i++)
      set_obj_coef(i, c[i]);
  }
  /** Set coefficient for a single column. */
  inline void set_obj_coef(int i, double v)
  {
    assert(i < get_num_cols());
    obj_coefs_[i] = v;
  }

  /** @} */

private:
  /**
   * Set object state for default constructor.
   *
   * This routine establishes the initial values of data fields in the
   * object when the object is created using the default constructor.
   */
  void set_initial_data();

  /* Objective */
  vector<double> obj_coefs_; /* Vector of objective coefficients. */
  char obj_sense_;

  /* Columns */
  vector<double> cols_lower_bounds_;
  vector<double> cols_upper_bounds_;

  /* Rows */
  vector<double> rows_lower_bounds_;
  vector<double> rows_upper_bounds_;
  vector<char> rows_senses_; /* Vector where each element represents
                               sense of corresponding row. */

  vector<set<int>*> col_to_row_mapping_;
  vector<set<int>*> row_to_col_mapping_;

  /* Constraint matrix */
  PackedMatrix cons_matrix_;
};

#endif /* __MILPP_HXX */
