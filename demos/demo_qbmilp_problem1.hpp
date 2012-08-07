// Copyright (c) 2012 Alexander Sviridenko

#include "les/quasiblock_milp_problem.hpp"

// This class represents the following quasi-block mixed integer liner
// programming demo problem #1:
//
// maximize 8x1 + 2x2 + 5x3 + 5x4 + 8x5 + 3x6 + 9x7 + 7x8 + 6x9
// subject to
//   2x1 + 3x2 + 4x3 +  x4                               <= 7
//    x1 + 2x2 + 3x3 + 2x4                               <= 6
//                x3 + 2x4 + 3x5 + 4x6 + 2x7             <= 9
//               2x3 +  x4 +  x5 + 2x6 + 3x7             <= 7
//                                       2x7 +  x8 + 2x9 <= 3
//                                       1x7 + 4x8 + 2x9 <= 5
class DemoQBMILPProblem1 : public QBMILPP
{
public:
  DemoQBMILPProblem1() {
    // Vector of objective function coefficients
    double c[] = {8.0, 2.0, 5.0, 5.0, 8.0, 3.0, 9.0, 7.0, 6.0};
    // Matrix of constraints
    double A[6][9] = {
      {2.0, 3.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0},
      {1.0, 2.0, 3.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0},
      {0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 2.0, 0.0, 0.0},
      {0.0, 0.0, 2.0, 1.0, 1.0, 2.0, 3.0, 0.0, 0.0},
      {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.0, 2.0},
      {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 4.0, 2.0},
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
    // Initialize problem
    initialize(c, 9, &A[0][0], 6, s, b);
  }

  ~DemoQBMILPProblem1() {
  }
};
