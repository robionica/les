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

from les import mp_model
from les import object_base

class DecomposerBase(object_base.ObjectBase):
  '''The base class for a general decomposer. Decomposer provides decomposition
  technique, so that: each submodel can be solved independently, the solution to
  the submodels can be combined to solve the original model.
  '''

  def __init__(self, model):
    object_base.ObjectBase.__init__(self)
    self._model = None
    self._decomposition_tree = None
    self._set_model(model)

  def get_model(self):
    '''Returns model being decomposed by this decomposer.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    '''
    return self._model

  def _set_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    self._model = model

  def decompose(self):
    '''Decomposes model and build decomposition tree. See also
    :func:`get_decomposition_tree` method.
    '''
    raise NotImplementedError()

  def get_decomposition_tree(self):
    '''Returns result decomposition tree, once the model has been
    decomposed or None otherwise.

    :returns: A :class:`~les.graphs.decomposition_tree.DecompositionTree`
      instance.
    '''
    return self._decomposition_tree
