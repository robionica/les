#include <les/demos/demo_qbmilpp.hpp>

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
QBMILPP*
gen_demo_qbmilpp()
{
  /* Vector of objective function coefficients */
  double c[] = {8.0, 2.0, 5.0, 5.0, 8.0, 3.0, 9.0, 7.0, 6.0};

  /* Matrix of constraints */
  double A[6][9] = {
    {2., 3., 4., 1., 0., 0., 0., 0., 0.},
    {1., 2., 3., 2., 0., 0., 0., 0., 0.},
    {0., 0., 1., 4., 3., 4., 2., 0., 0.},
    {0., 0., 2., 1., 1., 2., 5., 0., 0.},
    {0., 0., 0., 0., 0., 0., 2., 1., 2.},
    {0., 0., 0., 0., 0., 0., 3., 4., 1.},
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
  QBMILPP* p = new QBMILPP(c, 9, &A[0][0], 6, s, b);

  return p;
}
