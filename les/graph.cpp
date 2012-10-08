/*
 * Implements graph.hpp interface.
 *
 * Copyright (c) 2012 Oleksandr Sviridenko
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

#include <vector>

#include <boost/graph/graphviz.hpp>
#include <boost/graph/graph_utility.hpp>

#include "graph.hpp"

using namespace std;

void Graph::remove_vertex(int v)
{
  boost::clear_vertex(vertex(v), *this);
  boost::remove_vertex(vertex(v), *this);
}

void Graph::add_vertex(int vi)
{
  Graph::Vertex v = boost::add_vertex(*this);
  boost::put(boost::vertex_index, *this, v, vi);
}

void Graph::clone(Graph& g)
{
  // XXX: very straightforward implementation.
  // TODO: use boost::copy_graph()
  // g.clear(); // ?
  for (int i = 0; i < get_num_vertices(); i++) {
    Graph::Vertex v = boost::add_vertex(g);
    boost::put(boost::vertex_index, g, v, i);
  }

  boost::graph_traits<Graph>::edge_iterator ei, ei_end, next;
  boost::tie(ei, ei_end) = boost::edges(*this);
  for (next = ei; ei != ei_end; ei = next) {
    ++next;
    Graph::Vertex s = boost::source(*ei, *this);
    Graph::Vertex t = boost::target(*ei, *this);
    g.add_edge(boost::get(boost::vertex_index, *this, s),
               boost::get(boost::vertex_index, *this, t));
  }
}

void Graph::eliminate_vertex(int v)
{
  vector<int> vertices(1, v);
  eliminate_vertices(vertices);
}

void Graph::eliminate_vertices(vector<int>& vertices)
{
  for (vector<int>::iterator it = vertices.begin();
       it < vertices.end(); it++) {
    vector<int> neighbours = get_vertex_neighbours(*it);
    for (vector<int>::iterator first_nb = neighbours.begin();
         first_nb < neighbours.end(); first_nb++) {
      for (vector<int>::iterator second_nb = neighbours.begin();
           second_nb < neighbours.end(); second_nb++) {
        if (*first_nb != *second_nb) {
          add_edge(*first_nb, *second_nb);
        }
      }
    }
    remove_vertex(*it);
  }
}

vector<int> Graph::get_vertex_neighbours(int v)
{
  vector<int> nb;
  Graph::adjacency_iterator vi, vi_end;
  for (boost::tie(vi, vi_end) = boost::adjacent_vertices(vertex(v), *this);
       vi != vi_end; ++vi) {
    nb.push_back(boost::get(boost::vertex_index, *this, *vi));
  }
  return nb;
}

void Graph::dump()
{
  boost::print_graph(*this, boost::get(boost::vertex_index, *this));
#if 0 /* just another way to dump the graph */
  boost::write_graphviz(std::cout, *this);
#endif
}
