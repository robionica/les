#!/usr/bin/env python

from __future__ import absolute_import

import logging
from unittest import *

# By default turn off logging
logging.disable(logging.CRITICAL)

class TestCase(TestCase):

  assert_equal = TestCase.assertEqual
  assert_true = TestCase.assertTrue
  assert_false = TestCase.assertFalse
