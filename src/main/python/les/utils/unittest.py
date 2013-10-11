#!/usr/bin/env python
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

from __future__ import absolute_import

from numpy import testing
from unittest import *
from les.utils import logging

# By default turn off logging
logging.disable(logging.CRITICAL)

skip_if = skipIf

class TestCase(TestCase):
  """This class is a simple wrapper for unittest.TestCase class."""

  assert_almost_equal = TestCase.assertAlmostEqual
  assert_array_equal = testing.assert_array_equal
  assert_equal = TestCase.assertEqual
  assert_false = TestCase.assertFalse
  assert_is_none = TestCase.assertIsNone
  assert_is_not_none = TestCase.assertIsNotNone
  assert_list_equal = TestCase.assertListEqual
  assert_raises = TestCase.assertRaises
  assert_sequence_equal = TestCase.assertSequenceEqual
  assert_true = TestCase.assertTrue

  def setUp(self, *args, **kwargs):
    if hasattr(self, 'setup'):
      return self.setup(*args, **kwargs)
