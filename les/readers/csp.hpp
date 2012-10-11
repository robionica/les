/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#ifndef __LES_READERS_CSP_HPP
#define __LES_READERS_CSP_HPP

#include <boost/regex.hpp>
#include <vector>

/**
 * This reader initially written for A CSP Hypergraph Library. Each
 * hypergraph in the library is described in a text ﬁle in the
 * following format:
 *
 * Hyperedge 1 (Vertex 1 1, Vertex 1 2, ..., Vertex 1 n1),
 * Hyperedge 2 (Vertex 2 1, Vertex 2 2, ..., Vertex 2 n2),
 * .
 * .
 * .
 * Hyperedge m (Vertex m 1, Vertex m 2, ..., Vertex m nm).
 *
 * Note that the names of hyperedges and vertices may consist of any
 * combination of lower- and uppercase letters, numbers, underscore,
 * colon, etc. Comments start with '%' and continue until the end of
 * the line. Some ﬁles may also contain definitions within angle
 * brackets in the header.
 *
 * See <http://www.dbai.tuwien.ac.at/proj/hypertree/csphgl.pdf> to
 * learn more.
 */
class CSPReader
{
public:
  CSPReader()
  {
    _num_vertices = 0;
  };

  static const boost::regex COMMENT_EXPR;
  static const boost::regex HYPEREDGE_EXPR;

  void read(char* filename);

  inline int get_num_vertices() { return _num_vertices; }

  inline const PackedMatrix& get_adj_matrix() { return _adj_matrix; }

  void build_adj_matrix();

private:
  PackedMatrix _adj_matrix;
  int _num_vertices;
  vector< vector<int> > _hyperedges;
};

#endif /* __LES_READERS_CSP_HPP */
