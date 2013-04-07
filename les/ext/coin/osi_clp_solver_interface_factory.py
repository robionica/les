# Copyright (c) 2012-2013 Oleksandr Sviridenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from les.solvers.solver_factory import SolverFactory
from les.ext.coin.osi_clp_solver_interface import OsiClpSolverInterface

class OsiClpSolverInterfaceFactory(SolverFactory):
  """A producer of :class:`OsiClpSolverInterface`."""

  def __init__(self):
    SolverFactory.__init__(self)

  def build(self):
    """Returns new :class:`OsiClpSolverInterface` instance."""
    return OsiClpSolverInterface()
