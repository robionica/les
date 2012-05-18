/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#include <les/decomposition.hpp>
#include <les/finkelstein.hpp>

#undef LES_DEBUG

vector<DecompositionBlock*>*
FinkelsteinQBDecomposition::decompose_by_blocks(MILPP* problem)
{
  vector<set<int>*> U, S, M;
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
      for (set<int>::iterator u = U[i]->begin(); u != U[i]->end(); u++)
        {
          //printf("U%d\n", *u);
          PackedVector* row = problem->get_row(*u);

          if (i > 0)
            {
              for (set<int>::iterator s = S[i - 1]->begin();
                   s != S[i - 1]->end(); s++)
                {
                  if (row->get_element_by_index(*s) != 0.0)
                    left_part->set_coefficient(*u, *s,
                                               row->get_element_by_index(*s));
                }
            }

          for (set<int>::iterator m = M[i]->begin(); m != M[i]->end(); m++)
            {
              if (row->get_element_by_index(*m) != 0.0)
                middle_part->set_coefficient(*u, *m,
                                             row->get_element_by_index(*m));
            }
          //part->dump();
          if ((U.size() - i) > 1)
            {
              for (set<int>::iterator s = S[i]->begin();
                   s != S[i]->end(); s++)
                if (row->get_element_by_index(*s) != 0.0)
                  right_part->set_coefficient(*u, *s, row->get_element_by_index(*s));
            }
          //printf("\n");
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
                                      vector<set<int>*>* U,
                                      vector<set<int>*>* S,
                                      vector<set<int>*>* M)
{
  vector<set<int>*> S_; /* S' */
  vector<set<int>*> U_; /* U' */

  set<int>* cols_diff = NULL; /* cols delta */
  set<int>* cols = NULL;
  set<int>* prev_cols = NULL;
  set<int>* rows = NULL;

  bool merge_empty_blocks = true;

  /* If initial columns was not provided use default columns. */
  if (initial_cols == NULL)
    {
      /* Let us start from column 0. */
      initial_cols = new vector<int>(1, 0);
    }

  /* The first iteration will be implemented out of loop to avoid
     unnecessary if-statements. */
  cols = new set<int>(initial_cols->begin(), initial_cols->end());

  cols_diff = new set<int>();

  while (1)
    {
      prev_cols = cols;

      rows = problem->get_rows_related_to_cols(cols);
      assert(rows != NULL);

      cols = problem->get_cols_related_to_rows(rows);

      /* Stop creterion. Define whether we have to stop. */
      cols_diff->clear();

      set_difference(cols->begin(), cols->end(),
                     prev_cols->begin(), prev_cols->end(),
                     inserter(*cols_diff, cols_diff->begin()));
      if (cols_diff->empty())
        {
          break;
        }

      /* Store the new set of columns and variables */
      S_.push_back(cols);
      U_.push_back(rows);
    }
  free(cols_diff);

  if (U != NULL)
    {
      rows = U_.at(0);
      U->push_back(rows);

      for (vector<set<int>*>::iterator it = U_.begin() + 1; it != U_.end(); it++)
        {
          set<int>* u_diff = new set<int>();
          set_difference((*it)->begin(), (*it)->end(), rows->begin(), rows->end(),
                         inserter(*u_diff, u_diff->begin()));
          U->push_back(u_diff);
          rows = *it;
        }
    }

  /* Find all separators, where the separator is left/right
     part of a block. */
  if (S != NULL)
    {
      for (vector<set<int>*>::iterator it = U->begin(); it != U->end() - 1; it++)
        {
          set<int>* s = new set<int>(); /* separator */
          cols = problem->get_cols_related_to_rows(*(it + 1));
          prev_cols = problem->get_cols_related_to_rows(*it);
          set_intersection(cols->begin(), cols->end(),
                           prev_cols->begin(), prev_cols->end(),
                           inserter(*s, s->begin()));
          S->push_back(s);
        }
    }

  /* Find middle part for each block if required */
  if (M != NULL)
    {
      cols = problem->get_cols_related_to_rows(U->at(0));
      cols_diff = new set<int>();
      set_difference(cols->begin(), cols->end(),
                     S->at(0)->begin(), S->at(0)->end(),
                     inserter(*cols_diff, cols_diff->begin()));
      M->push_back(cols_diff);

      for (size_t i = 1; i < (U->size() - 1); i++)
        {
          set<int> sep_union;
          set_union(S->at(i - 1)->begin(), S->at(i - 1)->end(),
                    S->at(i)->begin(), S->at(i)->end(),
                    inserter(sep_union, sep_union.begin()));
          cols_diff = new set<int>();
          cols = problem->get_cols_related_to_rows(U->at(i));
          set_difference(cols->begin(), cols->end(),
                         sep_union.begin(), sep_union.end(),
                         inserter(*cols_diff, cols_diff->begin()));
          M->push_back(cols_diff);
        }

      cols = problem->get_cols_related_to_rows(*(U->end() - 1));
      cols_diff = new set<int>();
      set_difference(cols->begin(), cols->end(),
                     (*(S->end() - 1))->begin(), (*(S->end() - 1))->end(),
                     inserter(*cols_diff, cols_diff->begin()));
      M->push_back(cols_diff);
    }

#ifdef LES_DEBUG /* debug */
  printf("Finkelstein debug information:\n");
  for (size_t i = 0; i < S_.size(); i++)
    {
      cols = S_.at(i);
      printf(" S'%d : {", i);
      for (set<int>::iterator it = cols->begin(); it != cols->end(); it++)
        {
          printf("%d, ", *it);
        }
      printf("}\n");

      rows = U_.at(i);
      printf(" U'%d : {", i);
      for (set<int>::iterator it = rows->begin(); it != rows->end(); it++)
        {
          printf("%d, ", *it);
        }
      printf("}\n");
    }

  for (size_t i = 0; i < U->size(); i++)
    {
      rows = U->at(i);
      printf(" U%d  : {", i);
      for (set<int>::iterator it = rows->begin(); it != rows->end(); it++)
        {
          printf("%d, ", *it);
        }
      printf("}\n");
    }

  for (size_t i = 0; i < S->size(); i++)
    {
      cols = S->at(i);
      printf(" S%d  : {", i);
      for (set<int>::iterator it = cols->begin(); it != cols->end(); it++)
        {
          printf("%d, ", *it);
        }
      printf("}\n");
    }

  for (size_t i = 0; i < M->size(); i++)
    {
      cols = M->at(i);
      printf(" M%d  : {", i);
      for (set<int>::iterator it = cols->begin(); it != cols->end(); it++)
        {
          printf("%d, ", *it);
        }
      printf("}\n");
    }
#endif /* LED_DEBUG */
}
