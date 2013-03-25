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

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix, dok_matrix

class SparseVector(dok_matrix):

  def __init__(self, *args, **kwargs):
    dok_matrix.__init__(self, *args, **kwargs)

  def __iter__(self):
    rows, cols = dok_matrix.nonzero(self)
    for i in sorted(cols): # sorted!
      yield (i, self[i])

  def nonzero(self):
    return dok_matrix.nonzero(self)[1]

  def __setitem__(self, i, v):
    dok_matrix.__setitem__(self, (0, i), v)

  def __getitem__(self, i):
    return dok_matrix.__getitem__(self, (0, i))
