/*
 * Copyright (c) 2012 Alexander Sviridenko
 */
#include <iostream>

#include <les/quasiblock_milp_problem.hpp>
#include <les/finkelstein.hpp>
#include <les/demos/demo_qbmilpp.hpp>

#include <boost/foreach.hpp>

void
dump(const char* name, vector<set<int>*>& v)
{
  for (size_t i = 0; i < v.size(); i++)
    {
      std::cout << name
                << i
                << " : {";
      BOOST_FOREACH(int x, *v[i])
        {
          std::cout << x
                    << ", ";
        }
      std::cout << "}" << std::endl;
    }
}

int
main()
{
  /* Create quasiblock MILP problem and print it */
  QBMILPP* problem = gen_demo_qbmilpp();
  problem->print();

  /* Do finkelstein quasi-block decomposition and obtain decomposition
     information */
  vector<set<int>*> U, S, M;
  FinkelsteinQBDecomposition decomposer;
  decomposer.decompose(problem, NULL, &U, &S, &M);

  printf("Finkelstein decomposition information:\n");
  dump("U", U);

#if 0
  for (size_t i = 0; i < U.size(); i++)
    {
      std::cout << " U"
                << i
                << " : {";
      BOOST_FOREACH(int row, *U[i])
        {
          std::cout << row
                    << ", ";
        }
      std::cout << "}" << std::endl;
    }

  for (size_t i = 0; i < S.size(); i++)
    {
      std::cout << " S"
                << i
                << " : {";
      BOOST_FOREACH(int col, *S[i])
        {
          std::cout << col
                    << ", ";
        }
      std::cout << "}" << std::endl;
    }

  for (size_t i = 0; i < M.size(); i++)
    {
      std::cout << " M"
                << i
                << " : {";
      BOOST_FOREACH(int col, *M[i])
        {
          std::cout << col
                    << ", ";
        }
      std::cout << "}" 
                << std::endl;
    }
#endif
  return 0;
}
