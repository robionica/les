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

from les import linear_problem
from les.cli.commands import command_base

class Print(command_base.CommandBase):
  
  @classmethod
  def setup_argparser(self, argparser):
    pass
  
  def run(self):
    problem = linear_problem.build(self._args.file)
    problem.pprint()