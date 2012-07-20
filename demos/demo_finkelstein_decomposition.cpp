// Copyright (c) 2012 Alexander Sviridenko

#include <iostream>

#include <les/quasiblock_milp_problem.hpp>
#include <les/decomposition/finkelstein.hpp>

int
main()
{
/**
 * Problem:
 *
 * maximize 8x1 + 2x2 + 5x3 + 5x4 + 8x5 + 3x6 + 9x7 + 7x8 + 6x9
 * subject to
 *   2x1 + 3x2 + 4x3 +  x4                               <= 7
 *    x1 + 2x2 + 3x3 + 2x4                               <= 6
 *                x3 + 4x4 + 3x5 + 4x6 + 2x7             <= 9
 *               2x3 +  x4 +  x5 + 2x6 + 5x7             <= 7
 *                                       2x7 +  x8 + 2x9 <= 3
 *                                       3x7 + 4x8 +  x9 <= 5
 */
  /* Vector of objective function coefficients */
  double c[] = {8.0, 2.0, 5.0, 5.0, 9.0, 7.0, 6.0};

  /* Matrix of constraints */
  double A[6][7] = {
    {2., 3., 4., 1., 0., 0., 0.},
    {1., 2., 3., 2., 0., 0., 0.},
    {0., 0., 1., 4., 2., 0., 0.},
    {0., 0., 2., 1., 5., 0., 0.},
    {0., 0., 0., 0., 2., 1., 2.},
    {0., 0., 0., 0., 3., 4., 1.},
  };

  /* Vector of rows sense */
  char s[] = {
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER
  };

  /* Vector of right-hand side coefficients */
  double b[] = {
    7.0,
    6.0,
    9.0,
    7.0,
    3.0,
    5.0
  };

  /* Create quasi-block MILP problem by using predefined description.*/
  QBMILPP* problem = new QBMILPP(c, 7, &A[0][0], 6, s, b);

  /* Do finkelstein quasi-block decomposition and obtain decomposition
     information */
  vector< set<int> > U, S, M;

  FinkelsteinQBDecomposition decomposer;
  decomposer.decompose(problem, NULL, &U, &S, &M);
  cout << "Finkelstein decomposition information:" << endl;
  decomposer.dump();

  vector<QBMILPP*> subproblems = decomposer.get_subproblems();
  for (vector<QBMILPP*>::iterator it = subproblems.begin();
       it != subproblems.end(); it++)
    {
      QBMILPP* subproblem = *it;
      subproblem->dump();
    }

  return 0;
}
