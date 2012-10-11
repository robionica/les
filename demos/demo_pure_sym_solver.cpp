/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <iostream>

#include <coin/CoinPackedVector.hpp>
#include <coin/CoinPackedMatrix.hpp>
#include <coin/OsiSymSolverInterface.hpp>

#define N 7 /* Objective function size */
#define M 4 /* Number of constraints */

/* Objective function coefficients */
static double c[] = {2.0, 3.0, 1.0, 5.0, 4.0, 6.0, 1.0};

/* Matrix of constraints coefficients */
static double A[M][N] = {
  {3.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 2.0, 3.0, 3.0, 0.0, 0.0, 0.0},
  {0.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0},
  {0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 2.0},
};

/* Right-hand side (RHS) coefficients */
double b[] = {6.0, 5.0, 4.0, 5.0};

int
main()
{
  OsiSymSolverInterface si;
  /* Add variables to objective function and constraint matrix */
  for (int i = 0; i < N; i++) {
    /* Add new variable */
    CoinPackedVector col;
    si.addCol(col, 0.0, 1.0, c[i]);
    /* Set variable type */
    si.setInteger(i);
  }
  /* Add constraint */
  for (int i = 0; i < M; i++) {
    CoinPackedVector row(N, (double*)(&A[i][0]));
    si.addRow(row, 'L', b[i], 1.0);
  }
  const CoinPackedMatrix* matrix = si.getMatrixByRow();
  matrix->dumpMatrix();
  /* Maximization problem */
  si.setObjSense(-1.0);
  /* Set verbose level */
  si.setSymParam(OsiSymVerbosity, -2);
  /* Apply branch and bound method */
  si.branchAndBound();
  /* Print objective function value */
  std::cout << "Optimal objective function value = "
            << si.getObjValue()
            << std::endl;
  /* Print values of variables */
  std::cout << "Values of variables = ";
  const double* s = si.getColSolution();
  for (size_t i = 0; i < N; i++) {
    std::cout << s[i] << " ";
  }
  std::cout << std::endl;
}
