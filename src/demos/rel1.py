#!/usr/bin/env python
#
# Copyright (c) 2013 Oleksandr Sviridenko
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

import les
import les.utils.logging

def main():
  # Setup logging.
  les.utils.logging.get_logger().setLevel(les.utils.logging.DEBUG)
  # Build and optimize model.
  model = les.build_model()
  x1, x2, x3, x4, x5, x6, x7, x8, x9 = (model.add_binary_variable() for i in
                                        range(9))
  model.maximize(8 * x1 + 2 * x2 + 5 * x3 + 5 * x4 + 8 * x5 + 3 * x6 + 9 * x7
                 + 7 * x8 + 6 * x9)
  model.add_constraint(2 * x1 + 3 * x2 + 4 * x3 + x4 <= 7)
  model.add_constraint(x1 + 2 * x2 + 3 * x3 + 2 * x4 <= 6)
  model.add_constraint(x3 + 4 * x4 + 3 * x5 + 4 * x6 + 2 * x7 <= 9)
  model.add_constraint(2 * x3 + x4 + x5 + 2 * x6 + 5 * x7 <= 7)
  model.add_constraint(2 * x7 + x8 + 2 * x9 <= 3)
  model.add_constraint(3 * x7 + 4 * x8 + x9 <= 5)
  model.set_name('REL1')
  params = les.OptimizationParameters()
  params.relaxation_backend_solvers.append(les.OptimizationParameters.FRAKTIONAL_KNAPSACK_SOLVER)
  model.pprint()
  model.optimize(params)
  print 'Objective value:', model.get_objective_value()
  print 'Variables:'
  for var in model.get_variables():
    print '%15s = %f' % (var.get_name(), var.get_value())

if __name__ == '__main__':
  main()
