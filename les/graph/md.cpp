
#include <boost/config.hpp>
#include <boost/python.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/graph/minimum_degree_ordering.hpp>
#include <boost/graph/metis.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include <iostream>
#include <fstream>

using namespace std;

namespace boost { namespace python {

#define COPY_LIST(NAME) \
  { \
    stl_input_iterator<int> begin(NAME##_py), end; \
    std::copy(begin, end, back_inserter(NAME)); \
  }

typedef adjacency_list<vecS, vecS, directedS> Graph; 	// directed BGL graph
typedef graph_traits<Graph>::vertex_descriptor Vertex;
typedef std::vector<int> Vector;

std::vector<int>
minimum_degree_ordering(const object &xadj_py, const object &adjncy_py)
{
  int delta = 0;

  vector<int> xadj, adjncy;
  COPY_LIST(xadj);
  COPY_LIST(adjncy);
  
  Graph g(xadj.size() - 1);
  Vector iperm(xadj.size() - 1, 0);
  Vector perm(xadj.size() - 1, 0);
  Vector supernode_sizes(xadj.size() - 1, 1);
  Vector degree(xadj.size() - 1, 0);

  for (int i=0; i<xadj.size() - 1; i++)
  {
    int begin = xadj[i];
    int end = xadj[i+1];
    for (int j=begin; j<end; j++)
    {
#ifdef DEBUG
      cout << (i+1) <<  " -> " << (adjncy[j]+1) << endl;
#endif
      add_edge(i, adjncy[j], g);
    }
  }

  boost::property_map<Graph, vertex_index_t>::type id = get(vertex_index, g);

  boost::minimum_degree_ordering(g,
			  make_iterator_property_map(&degree[0], id, degree[0]),
			  &iperm[0],
			  &perm[0],
			  make_iterator_property_map(&supernode_sizes[0],
										 id, 
										 supernode_sizes[0]),
								 delta,
								 id
			  );

  return perm;
}

#if 0
std::vector<int> minimum_degree_ordering(char *fpath)
{
  int delta = 0;

  std::ifstream in_graph(fpath);
  graph::metis_reader reader(in_graph);
		
  Graph g(reader.begin(), reader.end(), reader.num_vertices());

  Vector iperm(reader.num_vertices(), 0);
  Vector perm(reader.num_vertices(), 0);
  Vector supernode_sizes(reader.num_vertices(), 1);
  Vector degree(reader.num_vertices(), 0);
	
  boost::property_map<Graph, vertex_index_t>::type id = get(vertex_index, g);

  boost::minimum_degree_ordering(g,
			  make_iterator_property_map(&degree[0], id, degree[0]),
			  &iperm[0],
			  &perm[0],
			  make_iterator_property_map(&supernode_sizes[0],
										 id, 
										 supernode_sizes[0]),
								 delta,
								 id
			  );

#ifdef DEBUG
  for (size_t i=0; i<reader.num_vertices(); i++)
  	printf("%d ", iperm[i]);
  printf("\n");
  for (size_t i=0; i<reader.num_vertices(); i++)
  	printf("%d ", perm[i]);
  printf("\n");
#endif
  return perm;
}
#endif

BOOST_PYTHON_MODULE(md)
{
  class_<std::vector<int> >("IntVec") .def(vector_indexing_suite<std::vector<int> >());

  def("md_ordering", minimum_degree_ordering);
}

} } // end namespace boost::graph::python

