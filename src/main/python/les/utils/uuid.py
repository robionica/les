from __future__ import absolute_import

import uuid


class ShortUUID(object):

  def __init__(self, alphabet=None):
    if alphabet is None:
      alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    self._alphabet = alphabet
    self._alpha_len = len(self._alphabet)

  def encode(self, unique_id):
    value = unique_id.int
    output = ""
    while value:
      value, digit = divmod(value, self._alpha_len)
      output += self._alphabet[digit]
    return output

  def uuid(self):
    unique_id = uuid.uuid4()
    return self.encode(unique_id)
