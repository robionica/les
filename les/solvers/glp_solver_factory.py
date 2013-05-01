from les.solvers.solver_factory import SolverFactory
from les.solvers.glp_solver import GLPSolver

class GLPSolverFactory(SolverFactory):

  def __init__(self):
    SolverFactory.__init__(self)

  def get_solver_class(self):
    return GLPSolver

  def build(self):
    return GLPSolver()
