// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied.  See the License for the specific language governing
// permissions and limitations under the License.

// Implements knapsak_problem.h interface.

#include <stdlib.h>
#include <stdio.h>

#include <les/knapsack_problem.hpp>

struct item {
  double m;
  int i; // item index
};

// Compare two items a and b from the bag. The items are comparing by their
static int
compare_items(const void* a, const void* b)
{
  return (int)(((struct item*) a)->m - ((struct item*) b)->m);
}

void
FractionalKnapsack::solve()
{
  double value;
  int i;
  int j;
  struct item* items;

  // Initialization
  j = get_num_items(); // start from the tail and move to the head
  _bag_weight = 0.;    // the bag's weight so far
  _bag_value = 0.;     // the bag's value so far
  PackedVector* weights = _problem->get_first_row();
  double max_weight = _problem->get_row_upper_bound(0);

  // Initialize the bag and items inside of it
  items = (struct item*)malloc(get_num_items() * sizeof(struct item));
  for (i = 0; i < get_num_items(); i++)
    {
      items[i].i = i;
      items[i].m = _problem->get_obj_coef(i) / weights->get_element(i);
    }
  // Sort the items by thier
  qsort(items, get_num_items(), sizeof(struct item), compare_items);

  while ((_bag_weight < max_weight) && (j >= 0))
    {
      i = items[--j].i;
      if ((_bag_weight + weights->get_element(i)) <= max_weight)
        {
          _bag_items[i] = 1.;
          _bag_weight += weights->get_element(i);
          _bag_value += (double)_problem->get_obj_coef(i);
        }
      else
        {
          _bag_items[i] = (double)(max_weight - _bag_weight)
            / weights->get_element(i);
          _bag_weight = (int)(weights->get_element(i) * _bag_items[i]);
          _bag_value += (double)_problem->get_obj_coef(i) * _bag_items[i];
          break;
        }
    }
  free(items);
}
