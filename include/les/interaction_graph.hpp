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

#include <les/graph.hpp>

class InteractionGraph : public boost::graph_t
{
public:
  /* Constructor */
  InteractionGraph(MILPP* problem);

  /* Return number of vertices in the graph. */
  inline size_t get_num_vertices() { return num_vertices(*this); }

  map< int, vector<int> > get_connected_components();
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
