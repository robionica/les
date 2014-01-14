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

from les.solution_tables import solution_tables_pb2
from les.solution_tables import sqlite_solution_table

SQLITE_SOLUTION_TABLE_ID = solution_tables_pb2.SQLITE_SOLUTION_TABLE

_SOLUTION_TABLE_MAP = {
  SQLITE_SOLUTION_TABLE_ID: sqlite_solution_table.SQLiteSolutionTable,
}

def get_instance_of(solution_table_id):
  if not isinstance(solution_table_id, int):
    raise TypeError()
  if not solution_table_id in _SOLUTION_TABLE_MAP:
    return None
  solution_table_class = _SOLUTION_TABLE_MAP[solution_table_id]
  return solution_table_class()
