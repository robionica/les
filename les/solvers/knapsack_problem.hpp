// Copyright (c) 2012 Alexander Sviridenko
//
// Knapsack problem.

#ifndef __LES_SOLVERS_KNAPSACK_PROBLEM_HPP
#define __LES_SOLVERS_KNAPSACK_PROBLEM_HPP

#include <les/solver.hpp>
#include <les/milp_problem.hpp>

// Given a collection of items G = {g_1, g_2,... , g_n}, where each item g_i =
// <v_i, w_i> worths v_i dollars, and weights w_i kgs, we would like to fill a
// bag with max-capacity of W kgs with items from G, so that the total value of
// items in the bag is maximized.
class FractionalKnapsack : MILPSolver {
public:
  // Constructor, where values is array of values, weights is array of weights,
  // n is number of items in the bag, max_weight is maximum weight that we can
  // carry in the bag.
  FractionalKnapsack(int* values, int* weights, size_t n, int max_weight) {
    _problem = new MILPP();
    // Convert vector of ints to doubles
    double* tmp_values = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) {
      tmp_values[i] = (double)values[i];
    }
    _problem->set_obj_coefs(tmp_values, n);
    free(tmp_values);
    _problem->set_obj_sense(MILPP::OBJ_SENSE_MAXIMISATION);
    // Convert vector of ints to doubles
    double* tmp_weights = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) {
      tmp_weights[i] = (double)weights[i];
    }
    free(tmp_weights);
    _problem->set_cons_matrix(tmp_weights, 1, n);
    _problem->set_row_upper_bound(0, (double)max_weight);
    // Setup the bag
    _bag_value = 0.;
    _bag_weight = 0.;
    _bag_items.clear();
  }

  void solve();

  inline MILPP* get_problem() {
    return _problem;
  }

  inline double get_obj_value() {
    return _bag_value;
  }

  inline size_t get_num_items() {
    return _problem->get_num_cols();
  }

  inline double get_bag_value() {
    return _bag_value;
  }

  inline double get_bag_weight() {
    return _bag_weight;
  }

  inline map<int, double>& get_bag_items() {
    return _bag_items;
  }

  //FractionalKnapsack::solve(int* values, int* weights, int W, unsigned n,
  //                          double* result_x, double* bag_value, double* bag_weight)

private:
  MILPP* _problem;
  // List of item indecies that was put to the bag
  map<int, double> _bag_items;
  double _bag_value;
  double _bag_weight;
};


#endif // __LES_SOLVERS_KNAPSACK_PROBLEM_HPP
