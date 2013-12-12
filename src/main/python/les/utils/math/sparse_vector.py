#!/usr/bin/env python

import numpy

class SparseVector(numpy.ndarray):

  def __new__(meta_class, *args, **kwargs):
    if not len(args):
      kwargs['shape'] = (kwargs.pop('size', 0), )
    else:
      return numpy.asarray(args[0]).view(meta_class)
    return numpy.ndarray.__new__(meta_class, **kwargs)

  copy_to_list = numpy.ndarray.tolist

  def get_entries_indices(self):
    """Returns indices of elements with nonzero values."""
    return self.nonzero()[0].tolist()

  def get_num_entries(self):
    return len(self.get_entries_indices())

  def get_size(self):
    return self.shape[0]

  def reserve(self, size):
    raise NotImplementedError()
