/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file interaction_graph.hpp
 * @brief Interaction graph
 */

#ifndef __INTERACTION_GRAPH_HXX
#define __INTERACTION_GRAPH_HXX

/* Include required BOOST API */
#include <boost/config.hpp>
#include <algorithm>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>
#include <boost/graph/biconnected_components.hpp>


#include <les/milp_problem.hpp>

namespace boost
{
  struct edge_component_t
  {
    enum { num = 555 };
    typedef edge_property_tag kind;
  };

  typedef adjacency_list< vecS, vecS, undirectedS, no_property,
                          property< edge_component_t, std::size_t > >graph_t;
  typedef graph_traits< graph_t >::vertex_descriptor vertex_t;
}

//typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS> graph_t;
//typedef boost::graph_traits<graph_t>::vertex_descriptor vertex_t;

class InteractionGraph : public boost::graph_t
{
public:
  /* Constructor */
  InteractionGraph(MILPP* problem);

  /* Return number of vertices in the graph. */
  inline size_t get_num_vertices() { return num_vertices(*this); }

  vector<int> get_connected_components();
  /** Return vector of vertex neighbors. */
  inline vector<int> get_vertex_neighbours(int v)
  {
    vector<int> nb;
    InteractionGraph::adjacency_iterator i, end;
    boost::tie(i, end) = adjacent_vertices(v, *this);
    for (; i != end; i++)
      {
        nb.push_back(*i);
      }
    return nb;
  }

  inline MILPP* get_problem()
  {
    return problem_;
  }

private:
  MILPP* problem_;
};

#endif /* __INTERACTION_GRAPH_HXX */
