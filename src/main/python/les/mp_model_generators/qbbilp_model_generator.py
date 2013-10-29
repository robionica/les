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

from scipy import sparse
import numpy
import random

from les import mp_model
from les.mp_model_generators import mp_model_generator_base
from les.utils import logging

class Range(tuple):

  def min(self):
    return self[0]

  def max(self):
    return self[1]

class BlockDescriptor(object):

  def __init__(self, num_constraints, num_variables,
               left_separator_size=0, right_separator_size=0):
    self.num_constraints = num_constraints
    self.num_variables = num_variables
    self.left_separator_size = left_separator_size
    self.right_separator_size = right_separator_size

  def __str__(self):
    return "BlockDescriptor[num_constraints=%d, num_variables=%d, " \
        "left_separator_size=%d, right_separator_size=%d]" \
        % (self.num_constraints, self.num_variables, self.left_separator_size,
           self.right_separator_size)

class QBBILPModelGenerator(mp_model_generator_base.MPModelGeneratorBase):

  # NOTE: some of parameters can be represented as a range (min, max). In this
  # case generator will take a random value from this range.
  default_params = {
    'num_constraints': (1, 10),
    'num_variables': (1, 10),
    'num_blocks': None,
    'dtype': float,
    'separator_size': 1,
    'fix_block_size': False,
    'block': {
      'num_constraints': (1, 10),
      'num_variables': (1, 10),
     }
  }

  def __init__(self):
    mp_model_generator_base.MPModelGeneratorBase.__init__(self)

  def _gen_fixed_size_blocks(self, m, n):
    blocks = []
    k = min(self._params['num_blocks']) and \
        random.randint(min(self._params['num_blocks']), max(self._params['num_blocks'])) or \
        max(self._params['num_blocks'])
    nn = n / k
    mm = m / k
    for i in range(k):
      blocks.append(BlockDescriptor(mm, nn))
    if n % k:
      blocks[-1].num_variables += n % k
    if m % k:
      blocks[-1].num_constraints += m % k
    return blocks

  def _gen_blocks(self, m, n):
    blocks = []
    if not m > 1 or not n > 3:
      return [BlockDescriptor(m, n)]
    while m > 1 and n > 3:
      nr = random.randint(1, round(m / 1.5))
      try:
        nc = random.randint(3, (n * nr) / m)
      except ValueError:
        nc = n
      blocks.append(BlockDescriptor(nr, nc))
      m -= nr
      n -= nc
    blocks[-1].num_constraints += m
    blocks[-1].num_variables += n
    return blocks

  @classmethod
  def fix_params(self, params):
    params = dict(self.default_params.items() + params.items())
    def _fix_range(v):
      return v and Range(not isinstance(v, tuple) and (None, v) or v) or None
    for key in ('num_constraints', 'num_variables', 'num_blocks',
                'separator_size'):
      params[key] = _fix_range(params[key])
    return params

  @classmethod
  def check_params(self, params):
    if not isinstance(params, dict):
      raise TypeError()
    if params['num_blocks'] and max(params['num_constraints']) < max(params['num_blocks']):
      logging.debug('Number of constraints cannot be less that number of blocks: %d < %d' \
                     % (max(params['num_constraints']), max(params['num_blocks'])))
      return False
    return True

  def gen(self, *args, **kwargs):
    """Generates a quasi-block BILP problem.

    :returns: A :class:`BILPProblem` instance with quasi-block structure or None.
    """
    params = (len(args) and isinstance(args[0], dict)) and args[0] or kwargs
    params = self.fix_params(params)
    if not self.check_params(params):
      return None
    self._params = params
    # Get problem shape
    (n, m) = (0, 0)
    n = min(params['num_variables']) and \
        random.randint(min(params['num_variables']), max(params['num_variables'])) or \
        max(params['num_variables'])
    m = min(params['num_constraints']) and \
        random.randint(min(params['num_constraints']), max(params['num_constraints'])) or \
        max(params['num_constraints'])
    if not params['num_blocks']:
      params['num_blocks'] = Range((1, int(m / 3)))
    self._matrix = sparse.dok_matrix((m, n), dtype=params['dtype'])
    self._rhs = [0.0] * m
    blocks = params['fix_block_size'] and \
        self._gen_fixed_size_blocks(m, n) or self._gen_blocks(m, n)
    # Start filling the matrix and rhs
    self._row_offset = 0
    self._col_offset = 0
    if min(params['separator_size']):
      # NOTE: separator size cannot be greater than number of variables in the
      # current block
      for i in xrange(len(blocks) - 1):
        sep_size = random.randint(
          min(params['separator_size']),
          min((min([blocks[i].num_variables, blocks[i + 1].num_variables]) / 2),
              max(params['separator_size']) / 2)
        )
        blocks[i].right_separator_size = blocks[i + 1].left_separator_size = sep_size
        self._fill_block(blocks[i])
    else:
      for i in xrange(len(blocks) - 1):
        sep_size = min((min([blocks[i].num_variables, blocks[i + 1].num_variables]) / 2),
                       max(params['separator_size']))
        blocks[i].right_separator_size = blocks[i + 1].left_separator_size = sep_size
        self._fill_block(blocks[i])
    self._fill_block(blocks[-1])
    # Build and return problem
    return mp_model.build(
      [random.randint(1, n) for i in xrange(n)],
      self._matrix.tocsr(),
      ['L'] * m,
      self._rhs
    )

  def _fill_block(self, b):
    num_variables = b.num_variables + b.right_separator_size
    s = num_variables * random.randint(1, 5)
    c = numpy.random.multinomial(s, [1. / num_variables for i in xrange(num_variables)],
                                 size=b.num_constraints)
    # Fix matrix, reduce zeros
    c += 1.
    s += num_variables
    for i in xrange(b.num_constraints):
      for j in xrange(num_variables):
        self._matrix[self._row_offset + i, self._col_offset + j] = c[i, j]
      self._rhs[self._row_offset + i] = s / (1.5 + random.random())
    self._row_offset += b.num_constraints
    self._col_offset += b.num_variables
