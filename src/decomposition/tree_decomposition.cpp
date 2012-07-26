// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied.  See the License for the specific language governing
// permissions and limitations under the License.

#include <les/decomposition.hpp>

#include <boost/graph/copy.hpp>
#include <boost/property_map/property_map.hpp>
#include <boost/graph/properties.hpp>

/* See <http://www.treewidth.com/> */

void
PermutationToTreeDecomposition::decompose(const vector<int>& permutation,
                                          int permutation_index)
{
  size_t size = _h.get_num_vertices();
  Bag bag;

  if (size == 2)
    {
      boost::graph_traits<Graph>::vertex_iterator vit, vit_end;
      for (boost::tie(vit, vit_end) = _h.get_vertices(); vit != vit_end; ++vit)
        {
          bag.push_back(boost::get(boost::vertex_index, _h, *vit));
        }
    }

  else
    {
      /* take next vertex from elimination ordering */
      int v = permutation[permutation_index];
      /* catch neighbours of eliminated vertex */
      vector<int> neighbours = _h.get_vertex_neighbours(v);
      /* compute the graph obtained from H by eliminating v */
      _h.eliminate_vertex(v);
      cout << ">>>" << v << endl;
      _h.dump();
      /* go into recursion */
      decompose(permutation, permutation_index + 1);
      /* create a bag and add it to the decomposition */
      bag.push_back(v);
      int lowest_index = 6000; /* Max integer value */
      int lowest_nb = -1; /* the lowest numbered neighbor of v */
      //vector<int> neighbours = _g->get_vertex_neighbours(v);
      for (vector<int>::iterator nb = neighbours.begin();
           nb < neighbours.end(); nb++)
        {
          bag.push_back(*nb);
          if (vertex_permutation_index[*nb] < lowest_index)
            {
              lowest_index = vertex_permutation_index[*nb];
              lowest_nb = *nb;
            }
        }

      /* create an edge between the bag and the neighborhood bag */
      if (lowest_nb > -1)
        {
          /* TODO */
        }
    }
  _bags.push_back(bag);
}

void
PermutationToTreeDecomposition::dump()
{
  for (vector<Bag>::iterator bit = _bags.begin(); bit < _bags.end();
       ++bit)
    {
      cout << "Bag#" << (bit - _bags.begin()) << ": ";
      for (vector<int>::iterator vit = (*bit).begin(); vit < (*bit).end();
           ++vit)
        {
          cout << (*vit + 1) << ", ";
        }
      cout << endl;      
    }
}

void
PermutationToTreeDecomposition::decompose(Graph& g,
                                          const vector<int>& permutation)
{
  assert(permutation.size() == g.get_num_vertices());

  /* First of all we need to check trivial case when n = 1 */
  if (g.get_num_vertices() == 1)
    {
      assert(1 == 2);
    }

  /* Clone initial graph to temporary graph */
  _g = &g;
  g.clone(_h);
  vertex_permutation_index.clear();
  for (size_t vi = 0; vi < _h.get_num_vertices(); vi++)
    {
      vertex_permutation_index[ permutation[vi] ] = vi;
    }
  /* Run first decomposition iteration */
  decompose(permutation, 0);
}
