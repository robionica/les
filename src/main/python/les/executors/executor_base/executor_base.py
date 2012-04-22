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

class ExecutorBase(object):
  '''This is base class for all executors. The executor executes tasks generated
  by pipeline and monitors them in prodaction. Once the task has been performed
  the result will be sent back to pipeline.
  '''

  def __init__(self, pipeline):
    from les import _pipeline
    if not isinstance(pipeline, _pipeline.Pipeline):
      raise TypeError()
    self._pipeline = pipeline

  def get_pipeline(self):
    '''Returns pipeline being used by this executor.

    :returns: A :class:`~les.pipeline.pipeline.Pipeline` instance.
    '''
    return self._pipeline

  def run(self):
    raise NotImplementedError()
