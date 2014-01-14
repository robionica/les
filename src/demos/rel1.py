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
import les.backend_solvers


def main():
  builder = les.MPModelBuilder()
  x1, x2, x3, x4, x5, x6, x7, x8, x9 = (builder.add_binary_variable() for i in
                                        range(9))
  model = (builder.maximize(8 * x1 + 2 * x2 + 5 * x3 + 5 * x4 + 8 * x5 + 3 * x6
                            + 9 * x7 + 7 * x8 + 6 * x9, "PROFIT")
           .set_constraints([2 * x1 + 3 * x2 + 4 * x3 + x4 <= 7,
                             x1 + 2 * x2 + 3 * x3 + 2 * x4 <= 6,
                             x3 + 4 * x4 + 3 * x5 + 4 * x6 + 2 * x7 <= 9,
                             2 * x3 + x4 + x5 + 2 * x6 + 5 * x7 <= 7,
                             2 * x7 + x8 + 2 * x9 <= 3,
                             3 * x7 + 4 * x8 + x9 <= 5])
           .set_name("REL1")
           .build())
  model.pprint()
  params = les.OptimizationParameters()
  params.driver.local_elimination_driver_parameters.relaxation_backend_solvers.append(les.backend_solvers.FRAKTIONAL_KNAPSACK_SOLVER_ID)
  model.optimize(params)
  print "Objective value:", model.get_objective_value()
  print "Variables:"
  for i in range(model.get_num_columns()):
    print("%15s = %f" % (model.columns_names[i], model.columns_values[i]))


if __name__ == '__main__':
  main()
