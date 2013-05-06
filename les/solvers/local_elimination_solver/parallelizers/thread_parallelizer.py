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

import logging
import time

from les import runtime
from les.runtime import thread_pool
from les.solvers.local_elimination_solver.parallelizers.parallelizer import Parallelizer

class ThreadParallelizer(Parallelizer):

  logger = logging.getLogger()

  def __init__(self, max_num_threads=0, reporter=None):
    Parallelizer.__init__(self)
    self._max_num_threads = 0
    self._reporter = reporter or self.default_reporter
    self.set_max_num_threads(max_num_threads or runtime.get_num_cpus())
    self._subproblems = []

  def __str__(self):
    return "%s[max_num_threads=%d, num_tasks=%d]" \
        % (self.__class__.__name__, self.get_max_num_threads(),
           len(self._subproblems))

  def set_max_num_threads(self, n):
    if not isinstance(n, (int, long)):
      raise TypeError()
    self._max_num_threads = n

  def get_max_num_threads(self):
    return self._max_num_threads

  @classmethod
  def default_reporter(cls, request, elapsed_time):
    subproblem = request.args[0]
    cls.logger.info("T%d: %s solved in %6.4f sec(s)"
                     % (request.requestID, subproblem, elapsed_time))

  def put(self, subproblem):
    """Put subproblems in order they come."""
    self._subproblems.append(subproblem)

  def _callback(self, subproblem):
    start = time.clock()
    solver = self._local_solver_factory.build()
    solver.solve(subproblem)
    return time.clock() - start

  def run(self):
    self.logger.info("Running %s..." % self)
    pool = thread_pool.ThreadPool(self._max_num_threads)
    reqs = thread_pool.make_requests(self._callback, self._subproblems,
                                     self._reporter)
    map(pool.put_request, reqs)
    pool.wait()
