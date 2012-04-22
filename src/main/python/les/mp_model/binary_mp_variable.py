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

from les.mp_model import mp_variable

class BinaryMPVariable(mp_variable.MPVariable):
  '''This class represents binary variable (also known as a dummy variable,
  indicator variable, design variable, Boolean indicator, categorical variable).

  :param name: The string that represents variable name.
  '''

  def __init__(self, name=None):
    mp_variable.MPVariable.__init__(self, 0.0, 1.0,
                                    mp_variable.MPVariable.BINARY, name)
