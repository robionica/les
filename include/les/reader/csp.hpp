/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

#ifndef __LES_READER_CSP_HPP
#define __LES_READER_CSP_HPP

#include <boost/regex.hpp>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>

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

  void read(char* filename)
  {
    std::ifstream file(filename);
    std::string line;

    std::map<std::string, int> vertex_names;
    int next_vertex_id = 0;

    while(std::getline(file, line))
      {
        boost::smatch res;
        /* Skip comments */
        if (boost::regex_match(line, res, COMMENT_EXPR,
                               boost::match_default | boost::match_partial))
          continue;
        if (boost::regex_match(line, res, HYPEREDGE_EXPR, boost::match_default))
          {
            boost::regex separator("\\s*,\\s*");

            std::vector<int> hyperedge;

            std::string vertices_list = std::string(res[2]);
            boost::sregex_token_iterator i(vertices_list.begin(),
                                           vertices_list.end(), separator, -1);
            boost::sregex_token_iterator j;

            while (i != j)
              {
                std::string vertex_name(*i++);
                if (!vertex_names.count(vertex_name))
                  {
                    vertex_names[vertex_name] = next_vertex_id;
                    next_vertex_id++;
                    //cout << vertex_name << endl;
                  }
                hyperedge.push_back( vertex_names[vertex_name] );
              }
            _hyperedges.push_back(hyperedge);
          }
        else {
          assert("Cannot recognise string");
        }
        //cout << line << endl;
      }

    _num_vertices = next_vertex_id;
    //cout << "Num vertices:" << get_num_vertices() << endl;

    build_adj_matrix();
  }

  inline int get_num_vertices() { return _num_vertices; }

  inline const PackedMatrix& get_adj_matrix() { return _adj_matrix; }

  void build_adj_matrix()
  {
    int cons = 0;
    vector< vector<int> >::iterator hyperedge;
    vector<int>::iterator vertex;
    for (hyperedge = _hyperedges.begin() ; hyperedge < _hyperedges.end();
         hyperedge++)
      {
        vector<int> vertices = *hyperedge;
        for (vertex = vertices.begin(); vertex < vertices.end(); vertex++)
          _adj_matrix.set_coefficient(cons, *vertex, 1.0);
        cons++;
      }
  }

private:
  PackedMatrix _adj_matrix;
  int _num_vertices;
  vector< vector<int> > _hyperedges;
};

const boost::regex CSPReader::COMMENT_EXPR = boost::regex("^\\s*%(.*?)$");
const boost::regex CSPReader::HYPEREDGE_EXPR = boost::regex("\\s*([a-zA-Z0-9:]+)\\s*\\((.*)\\)[\\,|\\.]\\s*");

#endif /* __LES_READER_CSP_HPP */
