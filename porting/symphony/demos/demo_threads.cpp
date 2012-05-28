
#include <iostream>

#include <les/quasiblock_milp_problem.hpp>
#include <les/finkelstein.hpp>
#include <OsiLeSolverInterface.hpp>

#include <boost/thread/thread.hpp>
#include <boost/foreach.hpp>
#include <boost/timer.hpp>

class BlockSolver
{
public:
  BlockSolver(DecompositionBlock* block)
    : _block(block)
  {
  }

  void operator()() const
  {
    OsiLeSolverInterface solver;
    //boost::timer::auto_cpu_timer t;
    boost::timer t;
    solver.solve_block(_block);
    cout << boost::this_thread::get_id()
         << " worked "
         << t.elapsed()
         << "s" << endl;
    // Report will be printed automatically
  }

private:
  DecompositionBlock* _block;
};

int
main()
{
  /* Vector of objective function coefficients */
  double c[] = {8.0, 2.0, 5.0, 5.0, 8.0, 3.0, 9.0, 7.0, 6.0};
  /* Matrix of constraints */
  double A[6][9] = {
    {2., 3., 4., 1., 0., 0., 0., 0., 0.},
    {1., 2., 3., 2., 0., 0., 0., 0., 0.},
    {0., 0., 1., 4., 3., 4., 2., 0., 0.},
    {0., 0., 2., 1., 1., 2., 5., 0., 0.},
    {0., 0., 0., 0., 0., 0., 2., 1., 2.},
    {0., 0., 0., 0., 0., 0., 3., 4., 1.},
  };
  /* Vector of rows sense */
  char s[] = {
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER,
    MILPP::ROW_SENSE_LOWER
  };
  /* Vector of right-hand side coefficients */
  double b[] = {
    7.0,
    6.0,
    9.0,
    7.0,
    3.0,
    5.0
  };

  /* Create quasiblock MILP problem by using predefined description.*/
  QBMILPP problem(c, 9, &A[0][0], 6, s, b);
  problem.set_obj_sense(QBMILPP::OBJ_SENSE_MAXIMISATION);
  /* Display the problem to verify the data */
  problem.print();

  /* Do finkelstein quasi-block decomposition and obtain decomposition
     information in form of chain of blocks. */
  FinkelsteinQBDecomposition decomposer;
  vector<DecompositionBlock*>* blocks = decomposer.decompose_by_blocks(&problem);

  for (vector<DecompositionBlock*>::iterator it = blocks->begin();
       it < blocks->end(); it++)
    {
      DecompositionBlock* block = *it;
      printf("<%p>\n", block);
    }

  return 0;

  OsiLeSolverInterface solver;

  boost::thread_group threads;
  BOOST_FOREACH(DecompositionBlock* block, *blocks)
    {
      boost::thread *t = new boost::thread(BlockSolver(block));
      threads.add_thread(t);
    }
  threads.join_all();
  return 0;
  solver.solve(blocks);

  std::cout << "Objective value = "
            << solver.get_obj_value()
            << std::endl;

  std::cout << "Solution: ";
  for (int i = 0; i < problem.get_num_cols(); i++)
    std::cout << solver.get_col_value(i)
              << " ";
  std::cout << std::endl;

  return 0;
}
