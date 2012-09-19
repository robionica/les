// Copyright (c) 2012 Alexander Sviridenko

#include "les/milp_problem.hpp"

// This class represents the following mixed integer liner
// programming demo problem #2:
//
// maximize 2x0 + 3x1 + x2 + 5x3 + 4x4 + 6x5 + x6
// subject to
//   3x0 + 4x1 +  x2                          <= 6
//         2x1 + 3x2 + 3x3                    <= 5
//         2x1             + 3x4              <= 4
//               2x2             + 3x5 + 2x6  <= 5
class DemoMILPProblem2 : public MILPP
{
public:
  DemoMILPProblem2() {
    // Vector of objective function coefficients
    double c[] = {2.0, 3.0, 1.0, 5.0, 4.0, 6.0, 1.0};
    // Matrix of constraints
    double A[4][7] = {
      {3.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0},
      {0.0, 2.0, 3.0, 3.0, 0.0, 0.0, 0.0},
      {0.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0},
      {0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 2.0},
    };

    // Vector of rows sense
    char s[] = {
      MILPP::ROW_SENSE_LOWER,
      MILPP::ROW_SENSE_LOWER,
      MILPP::ROW_SENSE_LOWER,
      MILPP::ROW_SENSE_LOWER
    };
    // Vector of right-hand side coefficients
    double b[] = {
      6.0,
      5.0,
      4.0,
      5.0
    };
    // Initialize problem
    initialize(c, 7, &A[0][0], 4, s, b);
    set_obj_sense(MILPP::OBJ_SENSE_MAXIMISATION);
  }

  ~DemoMILPProblem2() {
  }
};
