
#include <les/finkelstein.hpp>
#include <les/reader/celar.hpp>
#include <les/interaction_graph.hpp>

#include <boost/foreach.hpp>
#include <boost/graph/graphviz.hpp>

void
dump(const vector< set<int> >& U, const vector< set<int> >& S,
     const vector< set<int> >& M)
{
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

int
main(int argc, char* argv[])
{
  if (argc < 5)
    {
      cout << "USAGE: demo_celar_reader <VAR.TXT> <DOM.TXT> <CTR.TXT> <CST.TXT>"
           << endl;
      return 1;
    }

  CELARReader reader = CELARReader();
  reader.read(argv[1], /* var.txt */
              argv[2], /* dom.txt */
              argv[3], /* ctr.txt */
              argv[4]  /* cst.txt */
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
  map< int, vector<int> > components = g.get_connected_components();

  for (map< int, vector<int> >::iterator it = components.begin();
       it != components.end(); it++)
    {
      cout << "Decompose connected component #"
           << (*it).first << " (" << (*it).second.size() << " cols)"
           << endl;

      if ((*it).second.size() < 2)
        continue;

      /* Do finkelstein quasi-block decomposition and obtain
         decomposition information */
      vector< set<int> > U, S, M;
      FinkelsteinQBDecomposition decomposer;
      vector<int> initial_cols(1, (*it).second[0]);
      decomposer.decompose(&problem, &initial_cols, &U, &S, &M, 10, true);
      dump(U, S, M);
    }

  return 0;
}
