# -*- coding: utf-8; -*-
#
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

import types

class Problem(object):
  """Base problem class for all available problems."""

  subproblem_name_format = "Z%d"

  def __init__(self):
    self._name = None

  def set_name(self, name):
    """Sets problem name."""
    if not type(name) is types.StringType:
      raise TypeError()
    self._name = name

  def get_name(self):
    """Returns the problem name."""
    return self._name

  def build_subproblem(self, *args, **kwargs):
    """Builds and returns subproblem for the current problem instance."""
    raise NotImplementedError()

class Subproblem(Problem):

  pass
