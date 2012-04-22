#!/usr/bin/env python

import networkx

from les.graphs.ordering import minfill
from les.utils import unittest

class MinfillTest(unittest.TestCase):

  def test_ordering(self):
    g = networkx.Graph()
    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_node(6)
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(1, 0)
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(1, 4)
    g.add_edge(2, 0)
    g.add_edge(2, 1)
    g.add_edge(2, 3)
    g.add_edge(2, 5)
    g.add_edge(2, 6)
    g.add_edge(5, 6)
    n, ordering = minfill.minfill(g)
    self.assert_equal((0, 3, 4, 1, 2, 5, 6), ordering)

if __name__ == '__main__':
  unittest.main()
