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

#ifndef __LES_GRAPH_HPP
#define __LES_GRAPH_HPP

#include <iostream>
#include <algorithm>
#include <vector>

/* Include required BOOST API */
#include <boost/config.hpp>
#include <boost/graph/adjacency_list.hpp>

using namespace std;

namespace boost
{
  struct edge_component_t {
    enum { num = 555 };
    typedef edge_property_tag kind;
  };

  // See <http://www.boost.org/doc/libs/1_49_0/libs/graph/doc/graph_concepts.html>
  // and <http://www.boost.org/doc/libs/1_35_0/libs/graph/doc/adjacency_list.html>
  typedef adjacency_list< vecS, /* edge container */
                          listS, /* vertex container */
                          undirectedS, /* indirected graph */
                          property<vertex_index_t, int>, /* vertex properties */
                          property< edge_component_t, std::size_t > /* edge properties  */
                          >graph_t;
  typedef graph_traits< graph_t >::vertex_descriptor vertex_t;
}

class Graph : public boost::graph_t {
public:
  typedef boost::graph_traits<Graph>::vertex_descriptor Vertex;
  typedef boost::graph_traits<Graph>::edge_descriptor Edge;
  typedef boost::graph_traits<Graph>::adjacency_iterator
  adjacency_iterator;

  // Consructors
  Graph() { }

  Graph(size_t num_vertices) {
    for (size_t vi = 0; vi < num_vertices; vi++) {
      add_vertex(vi);
    }
  }

  /**
   * Returns number of vertices in the graph.
   */
  inline size_t get_num_vertices() {
    return boost::num_vertices(*this);
  }

  /* TODO: the method has to be improved. */
  /**
   * Returns vertex with index vi.
   */
  inline Graph::Vertex vertex(int vi) {
    //return boost::vertex(vi, *this); /* get vertex by position */
    boost::graph_traits<Graph>::vertex_iterator vit, vit_end, next;
    boost::tie(vit, vit_end) = boost::vertices(*this);
    for (next = vit; vit != vit_end; vit = next) {
      ++next;
      if (boost::get(boost::vertex_index, *this, *vit) == vi)
        return *vit;
    }
  }

  std::pair<vertex_iterator, vertex_iterator> get_vertices() {
    return boost::vertices(*this);
  }

  /**
   * Adds vertex.
   */
  void add_vertex(int vi);

  /**
   * Removes vertex.
   */
  void remove_vertex(int vi);

  inline bool has_edge(int vi1, int vi2) {
    return (boost::edge(vertex(vi1), vertex(vi2), *this).second ||
            boost::edge(vertex(vi2), vertex(vi1), *this).second);
  }

  /**
   * Adds and returns edge between vertices v1 and v2.
   */
  std::pair<Graph::Edge, bool> add_edge(int v1, int v2) {
    if (has_edge(v1, v2))
      return boost::edge(vertex(v1), vertex(v2), *this);
    return boost::add_edge(vertex(v1), vertex(v2), *this);
    //boost::put(boost::vertex_index, *this, vertex(v1), v1);
    //boost::put(boost::vertex_index, *this, vertex(v2), v2);
  }

  /**
   * Eliminates v is the operation, that adds an edge between
   * each pair of non-adjacent neighbours of v, and then removes v.
   */
  void eliminate_vertex(int v);
  void eliminate_vertices(vector<int>& vertices);

  /**
   * Returns vector of vertex neighbors.
   */
  vector<int> get_vertex_neighbours(int v);

  /**
   * Clones graph.
   */
  void clone(Graph& g);

  void dump();
};

#endif /* __LES_GRAPH_HPP */
