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

from .parallelizer_factory import ParallelizerFactory
from .thread_parallelizer import ThreadParallelizer

class ThreadParallelizerFactory(ParallelizerFactory):

  def __init__(self, max_num_threads=0, reporter=None):
    ParallelizerFactory.__init__(self)
    self._max_num_threads = max_num_threads
    self._reporter = reporter

  def build(self):
    return ThreadParallelizer(max_num_threads=self._max_num_threads,
                              reporter=self._reporter)
