/*
 * This file implements interaction_graph.hpp interface
 *
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

#include <les/interaction_graph.hpp>
#include <les/packed_vector.hpp>

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>

using namespace boost;

map< int, vector<int> >
InteractionGraph::get_connected_components()
{
  map< int, vector<int> > components;
#if 0
  vector<int> vertices_to_components(get_num_vertices());
  int num = boost::connected_components(*this, &vertices_to_components[0]);
  for (size_t i = 0; i < vertices_to_components.size(); i++) {
    components[ vertices_to_components[i] ].push_back(i);
  }
#endif
#if 0
  printf("Total number of components: %d\n", num);
  for (vector<int>::size_type i = 0; i != components.size(); ++i)
    printf("Vertex %d is in component %d\n", i, components[i]);
  printf("\n");
#endif

  return components;
}

InteractionGraph::InteractionGraph(MILPP* problem) : Graph(problem->get_num_cols())
{
  int ri; /* row index */
  int ci; /* col index */
  int ni; /* neighbor index */
  PackedVector* row;
  problem_ = problem;
  /* Start forming variable neighbourhoods by using constraints. */
  for (ri = 0; ri < problem->get_num_rows(); ri++) {
    row = problem->get_row(ri);
    for (ci = 0; ci < row->get_num_elements(); ci++) {
      for (ni = 0; ni < row->get_num_elements(); ni++) {
        if ((ci == ni) ||
            has_edge(row->get_index_by_pos(ci), row->get_index_by_pos(ni)))
          continue;
        add_edge(row->get_index_by_pos(ci),
                 row->get_index_by_pos(ni));
      }
    }
  }
}
