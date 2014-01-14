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

import types

from les.solution_tables import solution_table_base


class DataStore(object):
  '''This class represents interface to the actual data stores such as SQLite,
  MySQL, PostgreSQL, etc.
  '''

  def __init__(self, name):
    if not type(name) is types.StringType:
      raise TypeError('name must be a string')
    self._name = name

  def get_name(self):
    return self._name

  def get_connection(self):
    '''Attempts to establish connection with data store and returns Connection
    object.
    '''
    raise NotImplementedError()

class DBSolutionTableBase(solution_table_base.SolutionTableBase):
  '''Database based solution table.'''

  def __init__(self, data_store):
    solution_table_base.SolutionTableBase.__init__(self)
    if not isinstance(data_store, DataStore):
      raise TypeError()
    self._data_store = data_store

  def get_data_store(self):
    return self._data_store
