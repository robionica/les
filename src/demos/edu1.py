#!/usr/bin/env python
#
# Copyright (c) 2013 Oleksandr Sviridenko
#
# This demo formulates (in two different ways) and solves the following simple
# BILP model:
#
# maximize
#   8 x1 + 2 x2 + 5 x3 + 5 x4 + 8 x5 + 3 x6 + 9 x7 + 7 x8 + 6 x9
# subject to
#  2 x1 + 3 x2 + 4 x3 + x4 <= 7
#    x1 + 2 x2 + 3 x3 + 2 x4 <= 6
#                  x3 + 4 x4 + 3 x5 + 4 x6 + 2 x7 <= 9
#                  x3 +   x4 +   x5 + 2 x6 + 5 x7 <= 7
#                                            2 x7 +   x8 + 2 x9 <= 3
#                                            3 x7 + 4 x8 +   x9 <= 5
#
# It defines the problem and solves it once with help of C++ API and once with
# natural language API.

from les import *


def solve(model):
  model.pprint()
  model.optimize()
  print "Objective value:", model.get_objective_value()
  print "Variables:"
  for i in range(model.get_num_columns()):
    print("%15s = %f" % (model.columns_names[i], model.columns_values[i]))

def cpp_style_api():
  print "C++ style API"
  model = MPModelBuilder.build_from_scratch(
    [8, 2, 5, 5, 8, 3, 9, 7, 6],
    [[2, 3, 4, 1, 0, 0, 0, 0, 0],
     [1, 2, 3, 2, 0, 0, 0, 0, 0],
     [0, 0, 1, 4, 3, 4, 2, 0, 0],
     [0, 0, 2, 1, 1, 2, 5, 0, 0],
     [0, 0, 0, 0, 0, 0, 2, 1, 2],
     [0, 0, 0, 0, 0, 0, 3, 4, 1]],
    ['L'] * 6,
    [7, 6, 9, 7, 3, 5])
  solve(model)

def natural_language_api():
  print "Natural language API"
  builder = MPModelBuilder()
  x1, x2, x3, x4, x5, x6, x7, x8, x9 = (builder.add_binary_variable() for i in
                                        range(9))
  solve(builder.set_name("EDU1")
        .maximize(8 * x1 + 2 * x2 + 5 * x3 + 5 * x4 + 8 * x5 + 3 * x6
                  + 9 * x7 + 7 * x8 + 6 * x9, "PROFIT")
        .set_constraints([2 * x1 + 3 * x2 + 4 * x3 + x4 <= 7,
                          x1 + 2 * x2 + 3 * x3 + 2 * x4 <= 6,
                          x3 + 4 * x4 + 3 * x5 + 4 * x6 + 2 * x7 <= 9,
                          2 * x3 + x4 + x5 + 2 * x6 + 5 * x7 <= 7,
                          2 * x7 + x8 + 2 * x9 <= 3,
                          3 * x7 + 4 * x8 + x9 <= 5])
        .build())

if __name__ == '__main__':
  cpp_style_api()
  natural_language_api()
