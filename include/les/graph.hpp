
#ifndef __LES_GRAPH_HPP_H
#define __LES_GRAPH_HPP_H

/* Include required BOOST API */
#include <boost/config.hpp>
#include <algorithm>
#include <boost/graph/adjacency_list.hpp>

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

#endif /* __LES_GRAPH_HPP_H */
