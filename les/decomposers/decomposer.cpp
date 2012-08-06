// Copyright (c) 2012 Alexander Sviridenko

#include <stdio.h>
#include <set>

#include <les/decomposers/decomposer.hpp>
#include <les/interaction_graph.hpp>

set<int>*
DecompositionBlock::get_nonzero_rows() const
{
  set<int>* all_nonzero_rows = new set<int>();
  PackedMatrix* parts[] = {left_part_, middle_part_, right_part_};

  for (int i = 0; i < (sizeof(parts) / sizeof(PackedMatrix*)); i++)
    {
      vector<int>* nonzero_rows = parts[i]->get_nonzero_rows();
      all_nonzero_rows->insert(nonzero_rows->begin(),
                               nonzero_rows->end());
    }
  return all_nonzero_rows;
}

set<int>*
DecompositionBlock::get_nonzero_cols() const
{
  set<int>* all_nonzero_cols = new set<int>();
  PackedMatrix* parts[] = {left_part_, middle_part_, right_part_};

  for (int i = 0; i < (sizeof(parts) / sizeof(vector<int>*)); i++)
    {
      vector<int>* nonzero_cols = parts[i]->get_nonzero_cols();
      all_nonzero_cols->insert(nonzero_cols->begin(), nonzero_cols->end());
    }
  return all_nonzero_cols;
}
