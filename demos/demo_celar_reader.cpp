
#include <les/finkelstein.hpp>
#include <les/reader/celar.hpp>
#include <les/interaction_graph.hpp>

#include <boost/foreach.hpp>
#include <boost/graph/graphviz.hpp>

int
main()
{
  CELARReader reader = CELARReader();
  reader.read("../problems/CELAR/scen01/VAR.TXT", /* var.txt */
              "../problems/CELAR/scen01/DOM.TXT", /* dom.txt */
              "../problems/CELAR/scen01/CTR.TXT", /* ctr.txt */
              "../problems/CELAR/scen01/cst.txt"  /* cst.txt */
              );
  PackedMatrix cons_matrix = reader.get_cons_matrix();
  //cons_matrix.dump();

  MILPP problem;
  cout << "Initialize new MILP problem with "
       << cons_matrix.get_num_cols() << " cols and "
       << cons_matrix.get_num_rows() << " constraints"
       << endl;
  problem.initialize(cons_matrix.get_num_cols(),
                     cons_matrix.get_num_rows());
  problem.set_cons_matrix(&cons_matrix);

  /* Build interaction graph to check number of connected components. */
  InteractionGraph g = InteractionGraph(&problem);
  std::ofstream dotfile ("t.png");
  write_graphviz (dotfile, g);

  map< int, vector<int> > components = g.get_connected_components();

  for (map< int, vector<int> >::iterator it = components.begin();
       it != components.end(); it++)
    {
      cout << "Decompose connected component #"
           << (*it).first
           << endl;

      /* Do finkelstein quasi-block decomposition and obtain
         decomposition information */
      vector< set<int> > U, S, M;
      FinkelsteinQBDecomposition decomposer;
      vector<int> initial_cols(1, (*it).second[0]);
      decomposer.decompose(&problem, &initial_cols, &U, &S, &M, 10, true);

  for (size_t i = 0; i < U.size(); i++)
    {
      cout << " U"
           << i
           << " : {";
      BOOST_FOREACH(int row, U[i])
        {
          cout << row
               << ", ";
        }
      cout << "}" << std::endl;
    }

  for (size_t i = 0; i < S.size(); i++)
    {
      std::cout << " S"
                << i
                << " : {";
      BOOST_FOREACH(int col, S[i])
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
      BOOST_FOREACH(int col, M[i])
        {
          std::cout << col
                    << ", ";
        }
      std::cout << "}" 
                << std::endl;
    }

    }


  return 0;
}
