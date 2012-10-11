/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <iostream>
#include <fstream>
#include <map>
#include <string>

#include "csp.hpp"

const boost::regex CSPReader::COMMENT_EXPR = boost::regex("^\\s*%(.*?)$");
const boost::regex CSPReader::HYPEREDGE_EXPR = boost::regex("\\s*([a-zA-Z0-9:]+)\\s*\\((.*)\\)[\\,|\\.]\\s*");

void
CSPReader::build_adj_matrix()
{
  int cons = 0;
  vector< vector<int> >::iterator hyperedge;
  vector<int>::iterator vertex;
  for (hyperedge = _hyperedges.begin() ; hyperedge < _hyperedges.end();
       hyperedge++) {
      vector<int> vertices = *hyperedge;
      for (vertex = vertices.begin(); vertex < vertices.end(); vertex++) {
        _adj_matrix.set_coefficient(cons, *vertex, 1.0);
      }
      cons++;
  }
}

void
CSPReader::read(char* filename)
{
  std::ifstream file(filename);
  std::string line;
  std::map<std::string, int> vertex_names;
  int next_vertex_id = 0;

  while(std::getline(file, line)) {
    boost::smatch res;
    /* Skip comments */
    if (boost::regex_match(line, res, COMMENT_EXPR,
                           boost::match_default | boost::match_partial)) {
      continue;
    }
    if (boost::regex_match(line, res, HYPEREDGE_EXPR, boost::match_default)) {
      boost::regex separator("\\s*,\\s*");
      std::vector<int> hyperedge;
      std::string vertices_list = std::string(res[2]);
      boost::sregex_token_iterator i(vertices_list.begin(),
                                     vertices_list.end(), separator, -1);
      boost::sregex_token_iterator j;
      while (i != j) {
        std::string vertex_name(*i++);
        if (!vertex_names.count(vertex_name)) {
          vertex_names[vertex_name] = next_vertex_id;
          next_vertex_id++;
        }
        hyperedge.push_back( vertex_names[vertex_name] );
      }
      _hyperedges.push_back(hyperedge);
    } else {
      assert("Cannot recognise string");
    }
  }
  _num_vertices = next_vertex_id;
  build_adj_matrix();
}
