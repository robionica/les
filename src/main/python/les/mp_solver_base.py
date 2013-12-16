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

class MPSolverBase(object):
  """This class describes mathematical programming (MP) solver base class. This
  class is the base of all MP solver classes.
  """

  def load_model(self, model):
    """Loads model to the solver.

    :param model: A :class:`~les.mp_model.mp_model.MPModel` instance.
    """
    raise NotImplementedError()

  def get_solution(self):
    """Return primal solution.

    :returns:
    """
    raise NotImplementedError()

  def get_model(self):
    """Returns model solved by this solver.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    """
    raise NotImplementedError()

  def solve(self):
    """Starts model solving."""
    raise NotImplementedError()
