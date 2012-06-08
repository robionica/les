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
#include <les/graph/minimum_degree_ordering.hpp>

#include <boost/graph/minimum_degree_ordering.hpp>

#include <vector>

void
MinimumDegreeOrdering::run()
{
  vector<int> iperm(_g.get_num_vertices() - 1, 0);
  vector<int> perm(_g.get_num_vertices() - 1, 0);
  vector<int> supernode_sizes(_g.get_num_vertices() - 1, 1);
  vector<int> degree(_g.get_num_vertices - 1, 0);

  boost::property_map<Graph, vertex_index_t>::type id = get(vertex_index, g);

  boost::minimum_degree_ordering(_g,
                                 make_iterator_property_map(&degree[0], id, degree[0]),
                                 &iperm[0],
                                 &perm[0],
                                 make_iterator_property_map(&supernode_sizes[0],
                                                            id, 
                                                            supernode_sizes[0]),
								 delta,
								 id
			  );
}
