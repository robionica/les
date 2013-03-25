# -*- coding: utf-8; -*-
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

try:
  from pysqlite2 import dbapi2 as sqlite3
except ImportError:
  import sqlite3
import types

from les.data_models.db_data_model import DBDataModel, DataStore

class SQLiteDataStore(DataStore):
  """SQLite database interface wrapper."""

  def __init__(self, name=None, check_same_thread=True):
    DataStore.__init__(self, name or ":memory:")
    self._check_same_thread = check_same_thread
    self._connection = None
    if check_same_thread:
      self._connection = self._connect()

  def _connect(self, settings={}):
    return sqlite3.connect(self._name, check_same_thread=self._check_same_thread,
                           **settings)

  def get_connection(self, settings={}):
    """Returns Connection instance to SQLite database."""
    return self._connection and self._connection or self._connect(settings)


class SQLiteDataModel(DBDataModel):
  """This class represents data model based on SQLite DB."""

  def __init__(self, db_name=None):
    DBDataModel.__init__(self, SQLiteDataStore(db_name))

  def __del__(self):
    conn = self._data_store.get_connection()
    conn.commit()
    conn.close()

  def init(self, subproblems):
    for subproblem in subproblems:
      sql_script = "CREATE TABLE IF NOT EXISTS %s_solutions(%s, value DOUBLE, PRIMARY KEY (%s));\n" \
          % (subproblem.get_name(),
             ", ".join(["x%d INTEGER DEFAULT NULL" % i for i in subproblem.get_shared_cols() | subproblem.get_local_cols()]),
             ", ".join(["x%d" % i for i in subproblem.get_shared_cols()]))
      for another_subproblem, cols in subproblem.get_dependencies().items():
        sql_script += ";\n".join(["CREATE INDEX IF NOT EXISTS %s_index ON %s_solutions(%s);" \
                            % ("_".join(["x" + str(i) for i in cols]),
                               subproblem.get_name(),
                               ", ".join(["x" + str(i) for i in cols]))])
      self.get_data_store().get_connection().executescript(sql_script)

  def write_solution(self, subproblem, col_solution, obj_value):
    tbl_cols = []
    tbl_vals = []
    cols = subproblem.get_shared_cols() | subproblem.get_local_cols()
    tbl_name = subproblem.get_name() + "_solutions"

    if not subproblem.get_dependencies():
      tbl_cols = []
      tbl_vals = []
      for i in cols:
        tbl_cols.append("x%d" % i)
        tbl_vals.append(int(col_solution[i]))
      sql_stmt = "INSERT OR REPLACE INTO %s(%s, value) VALUES(%s)" \
          % (tbl_name, ", ".join(tbl_cols), ", ".join(["?"] * (len(cols) + 1)))
      print sql_stmt, tbl_vals + [float(obj_value)]
      self.get_data_store().get_connection().execute(sql_stmt, tbl_vals + [float(obj_value)])
      return

    dep_tbls = []
    deps = []
    where = []
    rcols = set()
    for sp, xcols in subproblem.get_dependencies().items():
      dep_tbls.append(sp.get_name() + "_s")
      rcols |= xcols
      for i in xcols:
        where.append("x%d=%d" % (i, col_solution[i]))
      deps.append("FROM %s_solutions %s_s WHERE %s" % (sp.get_name(), sp.get_name(), " AND ".join(where)))
    tbl_cols = []
    tbl_vals = []
    for i in cols:
      tbl_cols.append("x%d" % i)
      tbl_vals.append(int(col_solution[i]))
    sql_stmt = "INSERT OR REPLACE INTO %s(%s, value) SELECT %s + %s %s" \
        % (tbl_name, ", ".join(tbl_cols), ", ".join(map(str, tbl_vals + [obj_value])),
           " + ".join(["MAX("+name + ".value)" for name in dep_tbls]),
           " ".join(deps))
    print sql_stmt
    self._data_store.get_connection().execute(sql_stmt)

    return

    # Process shared columns
    where = []
    for i in shared_cols:
      where.append("x%d=%d" % (i, col_solution[i]))
          #tbl_cols.append("x%d" % i)
          #tbl_vals.append(int(col_solution[i]))
        # Process local columns
    for i in subproblem.get_local_cols():
      tbl_cols.append("x%d" % i)
      tbl_vals.append(str(int(col_solution[i])))
    # SQL
    sql_stmt = "INSERT OR REPLACE INTO solutions(%s, value) SELECT %s FROM solutions WHERE %s" \
        % (", ".join(tbl_cols), ", ".join(tbl_vals + [str(obj_value)]),
           " AND ".join(where))
        # self._data_store.execute(sql_stmt)
    print sql_stmt
