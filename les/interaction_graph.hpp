/*
 * Copyright (c) 2012 Alexander Sviridenko
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied.  See the License for the specific language governing
 * permissions and limitations under the License.
 */

#ifndef __LES_INTERACTION_GRAPH_HPP
#define __LES_INTERACTION_GRAPH_HPP

#include <algorithm>

/* Include required BOOST API */
#include <boost/config.hpp>
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

  /**
   * Compute and return the connected components of an undirected graph
   * using a DFS-based approach.
   *
   * Learn more:
   * http://www.boost.org/doc/libs/1_49_0/libs/graph/doc/connected_components.html
   */
  map< int, vector<int> > get_connected_components();

  inline MILPP* get_problem()
  {
    return problem_;
  }

private:
  MILPP* problem_;
};

#endif /* __INTERACTION_GRAPH_HPP */
