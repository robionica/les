// Copyright (c) 2012 Alexander Sviridenko

#ifndef __LES_KNAPSACK_PROBLEM_H
#define __LES_KNAPSACK_PROBLEM_H

// Given a collection of items G = {g_1, g_2,... , g_n}, where each item g_i =
// <v_i, w_i> worths v_i dollars, and weights w_i kgs, we would like to fill a
// bag with max-capacity of W kgs with items from G, so that the total value of
// items in the bag is maximized.
int
fractional_knapsack(int* v, int* weights, int W, unsigned n,
                    double** result_x, double* value, double* weight);

#endif // __LES_KNAPSACK_PROBLEM_H
