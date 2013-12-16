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

from les.decomposers import finkelstein_qb_decomposer
from les.decomposers import max_clique_decomposer
from les.decomposers import decomposers_pb2


FINKELSTEIN_QB_DECOMPOSER_ID = decomposers_pb2.QUASIBLOCK_FINKELSTEIN_DECOMPOSER
MAX_CLIQUE_DECOMPOSER_ID = decomposers_pb2.MAX_CLIQUE_DECOMPOSER

_DECOMPOSERS_TABLE = {
  FINKELSTEIN_QB_DECOMPOSER_ID: finkelstein_qb_decomposer.FinkelsteinQBDecomposer,
  MAX_CLIQUE_DECOMPOSER_ID: max_clique_decomposer.MaxCliqueDecomposer,
}


def get_instance_of(decomposer_id, *args, **kwargs):
  '''Returns an instance of the decomposer defined by `decomposer_id`, or `None`
  otherwise.
  '''
  if not isinstance(decomposer_id, int):
    raise TypeError()
  if not decomposer_id in _DECOMPOSERS_TABLE:
    return None
  decomposer_class = _DECOMPOSERS_TABLE[decomposer_id]
  return decomposer_class(*args, **kwargs)
