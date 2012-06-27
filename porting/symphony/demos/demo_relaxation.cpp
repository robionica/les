// Copyright (c) 2012 Alexander Sviridenko

#include <les/quasiblock_milp_problem.hpp>
#include <les/decomposition/finkelstein.hpp>

#include <OsiLeSolverInterface.hpp>

// 8x1 + 2x2 + 5x3 + 5x4 + 8x5 + 3x6 + 9x7 + 7x8 + 6x9 => max

int
main()
{
  QBMILPP* problem = new QBMILPP();

  double obj[] = {8., 2., 5., 5., 8., 3., 9., 7., 6.};
  problem->set_obj_coefs(&obj[0], 9);
  problem->set_obj_sense(QBMILPP::OBJ_SENSE_MAXIMISATION);

  double cons_matrix[] = {
    2., 3., 4., 1., 0., 0., 0., 0., 0.,
    1., 2., 3., 2., 0., 0., 0., 0., 0.,
    0., 0., 1., 2., 3., 4., 2., 0., 0.,
    0., 0., 2., 1., 1., 2., 3., 0., 0.,
    0., 0., 0., 0., 0., 0., 2., 1., 2.,
    0., 0., 0., 0., 0., 0., 1., 4., 2.,
  };
  problem->set_cons_matrix(cons_matrix, 6, 9);

  double rhs[] = {7., 6., 9., 7., 3., 5.};
  problem->set_rows_upper_bounds(rhs);

  problem->dump();

  FinkelsteinQBDecomposition* decomposer = new FinkelsteinQBDecomposition();
  vector<DecompositionBlock*>* blocks = decomposer->decompose_by_blocks(problem);
  delete decomposer;

  OsiLeSolverInterface* solver = new OsiLeSolverInterface();
  solver->solve(blocks);
  std::cout << "Objective value = "
            << solver->get_obj_value()
            << std::endl;

  std::cout << "Solution = ";
  for (int i = 0; i < problem->get_num_cols(); i++)
    std::cout << solver->get_col_value(i)
              << " ";
  std::cout << std::endl;
  delete solver;

  delete problem;

  return 0;
}
