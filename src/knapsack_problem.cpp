/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <stdlib.h>
#include <stdio.h>

struct item {
  double m;
  int i; /* item index */
};

/* Compare two items a and b from the bag. The items are comparing by
 their */
static int
compare_items(const void* a, const void* b)
{
  return (int)(((struct item*) a)->m - ((struct item*) b)->m);
}

/**
 * @v array of values
 * @w: array of weights
 * @max_w: maximum weight that we can carry in the bag
 * @n: number of items in the bag.
 */
int
fractional_knapsack(int* v, int* w, int max_w, unsigned n,
                    int** result_x, int* result_w)
{
  int* x;
  int t;
  int total_w;
  int i;
  int j;
  struct item* items;

  /* Allocate and initialize result vector. */
  x = (int*)calloc(n, sizeof(int));

  /* Initialize the bag and items inside of it */
  items = (struct item*)malloc(n * sizeof(struct item));
  for (i = 0; i < n; i++)
    {
      items[i].i = i;
      items[i].m = (double)v[i] / (double)w[i];
    }
  /* Sort the items by thier */
  qsort(items, n, sizeof(struct item), compare_items);

  j = n; /* start from the tail and move to the head */
  t = 0;
  total_w = 0; /* solution so far */
  while ((t < max_w) && (j >= 0))
    {
      i = items[--j].i;

      if ((t + w[i]) <= max_w)
        {
          x[i] = 1;
          t += w[i];
          total_w += v[i];
        }
      else
        {
          x[i] = (max_w - t) / w[i];
          t = max_w;
        }
    }

  *result_x = x;
  *result_w = total_w; /* result weight is current total weight */

  return 0;
}

#if 0
void
test_fractional_knapsack()
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
}

int
main()
{
  test_fractional_knapsack();
  return 0;
}
#endif
