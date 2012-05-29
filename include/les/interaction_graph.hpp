/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file interaction_graph.hpp
 * @brief Interaction graph
 */

#ifndef __INTERACTION_GRAPH_HPP
#define __INTERACTION_GRAPH_HPP

/* Include required BOOST API */
#include <boost/config.hpp>
#include <algorithm>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>
#include <boost/graph/biconnected_components.hpp>

#include <les/milp_problem.hpp>
#include <les/graph.hpp>

class InteractionGraph : public Graph
{
public:
  /* Constructor */
  InteractionGraph(MILPP* problem);

  map< int, vector<int> > get_connected_components();

  inline MILPP* get_problem()
  {
    return problem_;
  }

private:
  MILPP* problem_;
};

#endif /* __INTERACTION_GRAPH_HPP */
