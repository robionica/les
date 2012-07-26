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

/**
 * @file minimum_degree_ordering
 */

#ifndef __LES_GRAPH_MD_ORDERING_HPP
#define __LES_GRAPH_MD_ORDERING_HPP

#include <les/graph.hpp>

class Ordering
{
public:
  typedef vector<int> Permutation;

  Permutation& get_permutation();

};

/**
 * Uses http://www.boost.org/doc/libs/1_49_0/libs/graph/doc/minimum_degree_ordering.html
 */
class MinimumDegreeOrdering : public Ordering
{
public:
  inline Permutation& get_permutation()
  {
    return perm;
  }

private:
  Permutation perm;
};

#endif /* __LES_GRAPH_MD_ORDERING_HPP */
