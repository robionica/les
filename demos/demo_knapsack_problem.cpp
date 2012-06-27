// Copyright (c) 2012 Alexander Sviridenko

#include <stdio.h>

#include <les/knapsack_problem.h>

int
main()
{
  int v[] = {5, 4, 6, 1};
  int w[] = {3, 3, 3, 2};
  int W = 5;
  int* x;
  int s;
  int i;

  fractional_knapsack(v, w, W, 4, &x, &s);
  printf("Solution: %d\n", s);
  printf("Vector: ");
  for (i = 0; i < 4; i++)
    {
      printf("%d ", x[i]);
    }
  printf("\n");

  return 0;
}
