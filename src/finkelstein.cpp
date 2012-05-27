/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <les/decomposition.hpp>
#include <les/finkelstein.hpp>

#undef LES_DEBUG

vector<DecompositionBlock*>*
FinkelsteinQBDecomposition::decompose_by_blocks(MILPP* problem)
{
  vector< set<int> > U, S, M;
  PackedMatrix* left_part;
  PackedMatrix* middle_part;
  PackedMatrix* right_part;
  DecompositionBlock* next_block;
  DecompositionBlock* prev_block;
  vector<DecompositionBlock*>* blocks;

  blocks = new vector<DecompositionBlock*>();
  next_block = prev_block = NULL;

  /* Decompose a problem by using finkelstein algorithm */
  decompose(problem, NULL, &U, &S, &M);

  for (size_t i = 0; i < U.size(); i++)
    {
      next_block = new DecompositionBlock(problem);
      left_part = next_block->get_left_part();
      middle_part = next_block->get_middle_part();
      right_part = next_block->get_right_part();

      /* for each constraint */
      for (set<int>::iterator u = U[i].begin(); u != U[i].end(); u++)
        {
          //printf("U%d\n", *u);
          PackedVector* row = problem->get_row(*u);

          if (i > 0)
            {
              for (set<int>::iterator s = S[i - 1].begin();
                   s != S[i - 1].end(); s++)
                {
                  if (row->get_element_by_index(*s) != 0.0)
                    left_part->set_coefficient(*u, *s,
                                               row->get_element_by_index(*s));
                }
            }

          for (set<int>::iterator m = M[i].begin(); m != M[i].end(); m++)
            {
              if (row->get_element_by_index(*m) != 0.0)
                middle_part->set_coefficient(*u, *m,
                                             row->get_element_by_index(*m));
            }
          if ((U.size() - i) > 1)
            {
              for (set<int>::iterator s = S[i].begin();
                   s != S[i].end(); s++)
                if (row->get_element_by_index(*s) != 0.0)
                  right_part->set_coefficient(*u, *s, row->get_element_by_index(*s));
            }
        }

      if (prev_block)
      {
        //next_block->set_left_part(prev_block->get_right_part());
      }

      blocks->push_back(next_block);
      prev_block = next_block;
    }

  return blocks;
}

/**
 * By default initial_cols can be omitted. Thus default columns will
 * be stored.
 *
 * On this moment it returns nothing. Maybe we need some error status?
 */
void
FinkelsteinQBDecomposition::decompose(MILPP* problem,
                                      vector<int>* initial_cols,
                                      vector< set<int> >* U,
                                      vector< set<int> >* S,
                                      vector< set<int> >* M,
                                      int max_separator_size,
                                      bool merge_empty_blocks)
{
  vector< set<int> > S_; /* S' */
  vector< set<int> > U_; /* U' */

  set<int> cols_diff = set<int>();
  set<int> prev_cols = set<int>();
  set<int> rows = set<int>();

  /* If initial columns was not provided use default columns. */
  if (initial_cols == NULL)
    {
      /* Let us start from column 0. */
      initial_cols = new vector<int>(1, 0);
    }

  /* The first iteration will be implemented out of loop to avoid
     unnecessary if-statements. */
  set<int> cols = set<int>(initial_cols->begin(), initial_cols->end());

  while (1)
    {
      cols_diff.clear();
      rows = *problem->get_rows_related_to_cols(&cols);
      assert(!rows.empty());

      prev_cols = cols;
      cols = *problem->get_cols_related_to_rows(&rows);

      set_difference(cols.begin(), cols.end(),
                     prev_cols.begin(), prev_cols.end(),
                     inserter(cols_diff, cols_diff.begin()));

      /* Store the new set of columns and rows. We also need to store
         the last set even it will be empty. In some cases there might
         be exception such as blocks of right-separators. */
      S_.push_back(cols);
      U_.push_back(rows);

      if (cols_diff.empty())
        {
          break;
        }
    }

  rows = U_.at(0);
  U->push_back(rows);

  for (vector< set<int> >::iterator it = U_.begin() + 1; it != U_.end(); it++)
    {
      set<int> u_diff = set<int>();
      set_difference((*it).begin(), (*it).end(), rows.begin(), rows.end(),
                     inserter(u_diff, u_diff.begin()));
      U->push_back(u_diff);
      rows = *it;
    }

  /* Find all separators, where the separator is left/right
     part of a block. */
  if (S != NULL)
    {
      for (vector< set<int> >::iterator it = U->begin(); it != U->end() - 1; it++)
        {
          set<int> s = set<int>(); /* separator */
          set<int>& rows = *(it + 1);
          cols = *problem->get_cols_related_to_rows(&rows);
          set<int>& prev_rows = *it;
          prev_cols = *problem->get_cols_related_to_rows(&prev_rows);
          set_intersection(cols.begin(), cols.end(),
                           prev_cols.begin(), prev_cols.end(),
                           inserter(s, s.begin()));
          if (max_separator_size && s.size() > max_separator_size)
            {
              prev_rows.insert(rows.begin(), rows.end());
              U->erase(it + 1);
              it--;
              continue;
            }
          S->push_back(s);
        }
    }

  /* Find middle part for each block if required */
  if (M != NULL)
    {
      cols = *problem->get_cols_related_to_rows(&U->at(0));
      cols_diff.clear();

      set_difference(cols.begin(), cols.end(),
                     S->at(0).begin(), S->at(0).end(),
                     inserter(cols_diff, cols_diff.begin()));
      M->push_back(cols_diff);

      vector<int> e = vector<int>();

      for (size_t i = 1; i < (U->size() - 1); i++)
        {
          set<int> sep_union;

          cols_diff.clear();

          set_union(S->at(i - 1).begin(), S->at(i - 1).end(),
                    S->at(i).begin(), S->at(i).end(),
                    inserter(sep_union, sep_union.begin()));

          cols = *problem->get_cols_related_to_rows(&U->at(i));
          set_difference(cols.begin(), cols.end(),
                         sep_union.begin(), sep_union.end(),
                         inserter(cols_diff, cols_diff.begin()));
#if 0
          if (merge_empty_blocks && cols_diff.empty())
            {
              U->at(M->size() - 1).insert( U->at(i).begin(), U->at(i).end() );
              M->at(M->size() - 1).insert( S->at(i - 1).begin(), S->at(i - 1).end() );

              U->erase(U->begin() + i);
              S->erase(S->begin() + i - 1);
              i--;
              continue;
            }
#endif
          M->push_back(cols_diff);
        }

      cols = *problem->get_cols_related_to_rows(&(*(U->end() - 1)));
      cols_diff.clear();
      set_difference(cols.begin(), cols.end(),
                     (*(S->end() - 1)).begin(), (*(S->end() - 1)).end(),
                     inserter(cols_diff, cols_diff.begin()));
      M->push_back(cols_diff);

      if (merge_empty_blocks) {
        for (size_t i = 1; i < U->size(); i++)
          {
            if (!M->at(i).empty())
              continue;
            U->at(i - 1).insert( U->at(i).begin(), U->at(i).end() );
            M->at(i - 1).insert( S->at(i - 1).begin(), S->at(i - 1).end() );

            U->erase(U->begin() + i);
            M->erase(M->begin() + i);
            S->erase(S->begin() + i - 1);

            i--;
          }
      }
    }

  // DEBUG
  /* Verification */
  assert(U->size() == M->size());
  assert(U->size() == (S->size() + 1));
#if 1
  do {
    int num_rows = 0;
    for (vector< set<int> >::iterator it = U->begin(); it != U->end(); it++)
      num_rows += (*it).size();
    int num_cols = 0;
    for (vector< set<int> >::iterator it = S->begin(); it != S->end(); it++)
      num_cols += (*it).size();
    for (vector< set<int> >::iterator it = M->begin(); it != M->end(); it++)
      num_cols += (*it).size();
    //assert(problem->get_num_rows() == num_rows);
    //assert(problem->get_num_cols() == num_cols);
  } while (0);
#endif
}
