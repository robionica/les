// Copyright (c) 2012 Alexander Sviridenko

#include <stdio.h>
#include <sys/time.h>

#include <les/quasiblock_milp_problem.hpp>
#include <les/decomposition.hpp>
#include <OsiLeSolverInterface.hpp>

void
test1()
{
  // Vector of objective function coefficients
  double c[] = {2.0, 3.0, 1.0, 5.0, 4.0, 6.0, 1.0};
  // Matrix of constraints
  double A[4][7] = {
    {3., 4., 1., 0., 0., 0., 0.},
    {0., 2., 3., 3., 0., 0., 0.},
    {0., 2., 0., 0., 3., 0., 0.},
    {0., 0., 2., 0., 0., 3., 2.},
  };
  // Vector of rows sense
  char s[] = {
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
  };
  // Vector of right-hand side coefficients
  double b[] = {
    6.0,
    5.0,
    4.0,
    5.0
  };
  // Create quasiblock MILP problem by using predefined description.
  QBMILPP problem(c, 7, &A[0][0], 4, s, b);
  problem.set_obj_sense(QBMILPP::OBJ_SENSE_MAXIMISATION);
  // Show the problem on display to verify the data
  problem.dump();
  // Do finkelstein quasi-block decomposition and obtain decomposition
  //   information in form of chain of blocks.
  FinkelsteinQBDecomposition decomposer;
  vector<DecompositionBlock*>* blocks = decomposer.decompose_by_blocks(&problem);
  cout << "Finkelstein decomposition:" << endl;
  decomposer.dump();

  OsiLeSolverInterface solver;
  solver.solve(blocks);
  std::cout << "Objective value = " << solver.get_obj_value() << std::endl;
  std::cout << "Solution: ";
  for (int i = 0; i < problem.get_num_cols(); i++) {
    std::cout << solver.get_col_value(i) << " ";
  }
  std::cout << std::endl;
}

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
void
test2()
{
  // Vector of objective function coefficients
  double c[] = {8.0, 2.0, 5.0, 5.0, 8.0, 3.0, 9.0, 7.0, 6.0};
  // Matrix of constraints
  double A[6][9] = {
    {2., 3., 4., 1., 0., 0., 0., 0., 0.},
    {1., 2., 3., 2., 0., 0., 0., 0., 0.},
    {0., 0., 1., 4., 3., 4., 2., 0., 0.},
    {0., 0., 2., 1., 1., 2., 5., 0., 0.},
    {0., 0., 0., 0., 0., 0., 2., 1., 2.},
    {0., 0., 0., 0., 0., 0., 3., 4., 1.},
  };
  // Vector of rows sense
  char s[] = {
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER
  };
  // Vector of right-hand side coefficients
  double b[] = {
    7.0,
    6.0,
    9.0,
    7.0,
    3.0,
    5.0
  };

  // Create quasiblock MILP problem by using predefined description
  QBMILPP problem(c, 9, &A[0][0], 6, s, b);
  problem.set_obj_sense(QBMILPP::OBJ_SENSE_MAXIMISATION);
  // Display the problem to verify the data
  problem.dump();

  // Do finkelstein quasi-block decomposition and obtain decomposition
  // information in form of chain of blocks.
  FinkelsteinQBDecomposition decomposer;
  vector<DecompositionBlock*>* blocks = decomposer.decompose_by_blocks(&problem);

  OsiLeSolverInterface solver;
  solver.solve(blocks);
  std::cout << "Objective value = " << solver.get_obj_value() << std::endl;
  std::cout << "Solution: ";
  for (int i = 0; i < problem.get_num_cols(); i++)
    std::cout << solver.get_col_value(i) << " ";
  std::cout << std::endl;
}

int
main()
{
  test1();
  test2();
  return 0;
}
