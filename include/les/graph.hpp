/*
 * Copyright (c) 2012 Alexander Sviridenko
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
  struct edge_component_t
  {
    enum { num = 555 };
    typedef edge_property_tag kind;
  };

  typedef adjacency_list< vecS, /* edge container */
                          listS, /* vertex container */
                          undirectedS, /* indirected graph */
                          property<vertex_index_t, int>, /* no_property */ /* vertex properties */
                          property< edge_component_t, std::size_t > /* edge properties  */
                          >graph_t;
  typedef graph_traits< graph_t >::vertex_descriptor vertex_t;
}

class Graph : public boost::graph_t
{
public:

  /* Consructors */
  Graph() { }
  Graph(size_t num_cols) : boost::graph_t(num_cols)
  {
  }

  /** Return number of vertices in the graph. */
  inline size_t get_num_vertices() { return num_vertices(*this); }

  inline boost::vertex_t vertex(int v) { return boost::vertex(v, *this); }

  /** Remove vertex. */
  void remove_vertex(int v);

  std::pair<boost::graph_traits<Graph>::edge_descriptor, bool>
  add_edge(int v1, int v2)
  {
    if (!boost::edge(vertex(v1), vertex(v2), *this).second)
      {
        boost::add_edge(vertex(v1), vertex(v2), *this);
        boost::put(boost::vertex_index, *this, vertex(v1), v1);
        boost::put(boost::vertex_index, *this, vertex(v2), v2);
      }
  }

  /** Eliminate a vertex. Once vertex has been eliminated all the
     vertices connected to it are joined together (making the
     neighborhood of this variable into a clique in the remaining
     graph, before deleting), modifying the structure of the graph. */
  void eliminate_vertex(int v);
  void eliminate_vertices(vector<int>& vertices);

  /** Return vector of vertex neighbors. */
  inline vector<int> get_vertex_neighbours(int v)
  {
    vector<int> nb;
    typename boost::graph_traits< Graph >::adjacency_iterator vi, vi_end;
    //boost::graph_traits<Graph>::adjacency_iterator i, end;
    //boost::tie(i, end) = adjacent_vertices(v, *this);
    //for (; i != end; i++)
    for (boost::tie(vi, vi_end) = boost::adjacent_vertices(vertex(v), *this); vi != vi_end; ++vi)
      {
        nb.push_back(boost::get(boost::vertex_index, *this, *vi));
        //cout << boost::get(boost::vertex_index, *this, *vi) << endl;
      }
    return nb;
  }

  void dump();
};

#endif /* __LES_GRAPH_HPP */
