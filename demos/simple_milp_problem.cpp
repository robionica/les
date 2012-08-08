// Copyright (c) 2012 Alexander Sviridenko

#include <iostream>
#include <coin/CoinPackedVector.hpp>
#include <coin/CoinPackedMatrix.hpp>
#include <coin/OsiSymSolverInterface.hpp>

#define N 7 /* Количество переменных целевой функции */
#define M 4 /* Количество ограничений */

/* Массив коэффициентов целевой функции */
static double c[] = {2.0, 3.0, 1.0, 5.0, 4.0, 6.0, 1.0};

/* Матрица коэффициентов ограничений */
static double A[M][N] = {
  {3.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.0},
  {0.0, 2.0, 3.0, 3.0, 0.0, 0.0, 0.0},
  {0.0, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0},
  {0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 2.0},
};

/* Вектор правых ограничений */
double b[] = {6.0, 5.0, 4.0, 5.0};

int main()
{
  OsiSymSolverInterface si;

  /* Добавим переменные в целевую функцию
     и матрицу ограничений */
  for (int i = 0; i < N; i++)
    {
      /* Добавляем новую переменную */
      CoinPackedVector col;
      si.addCol(col, 0.0, 1.0, c[i]);
      /* Устанавливаем тип переменной */
      si.setInteger(i);
    }

  /* Добавляем ограничения */
  for (int i = 0; i < M; i++)
    {
      CoinPackedVector row(N, (double*)(&A[i][0]));
      si.addRow(row, 'L', b[i], 1.0);
    }

  const CoinPackedMatrix* matrix = si.getMatrixByRow();
  matrix->dumpMatrix();

  /* Решим задачу максимизации */
  si.setObjSense(-1.0);

  si.setSymParam(OsiSymVerbosity, -2);

  /* Применим метод ветвей и границ */
  si.branchAndBound();

  /* Выводим значение целевой функции */
  std::cout << "Оптимальное значение целевой функции = "
            << si.getObjValue()
            << std::endl;

  /* Выводим вектор значения переменных */
  std::cout << "Оптимальное значение переменных = ";
  const double* s = si.getColSolution();
  for (size_t i = 0; i < N; i++)
    std::cout << s[i] << " ";
  std::cout << std::endl;
}
