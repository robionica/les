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

import logging
try:
  from pysqlite2 import dbapi2 as sqlite3
except ImportError:
  import sqlite3
import types

from les.data_models.db_data_model import DBDataModel, DataStore

_MAX_TIMEOUT = 5.0

logger = logging.getLogger()

class SQLiteCursorWrapper(sqlite3.Cursor):
  """Substitutes sqlite3.Cursor, with a cursor that logs commands.

  Inherits from sqlite3.Cursor class and extends methods such as execute,
  executemany and execute script, so it logs SQL calls.
  """

  def execute(self, sql, *args):
    """Replaces execute() with a logging variant."""
    if args:
      parameters = []
      for arg in args:
        if isinstance(arg, buffer):
          parameters.append('<blob>')
        else:
          parameters.append(repr(arg))
      logger.debug('SQL Execute: %s - \n %s', sql,
                   '\n '.join(str(param) for param in parameters))
    else:
      logger.debug(sql)
    return super(SQLiteCursorWrapper, self).execute(sql, *args)

  def executemany(self, sql, seq_parameters):
    """Replaces executemany() with a logging variant."""
    seq_parameters_list = list(seq_parameters)
    logger.debug('SQL ExecuteMany: %s - \n %s', sql,
                  '\n '.join(str(param) for param in seq_parameters_list))
    return super(SQLiteCursorWrapper, self).executemany(sql,
                                                        seq_parameters_list)

  def executescript(self, sql):
    """Replaces executescript() with a logging variant."""
    logger.debug('SQL ExecuteScript: %s', sql)
    return super(SQLiteCursorWrapper, self).executescript(sql)

class SQLiteConnectionWrapper(sqlite3.Connection):
  """Substitutes sqlite3.Connection with a connection that logs commands.

  Inherits from sqlite3.Connection class and overrides cursor replacing the
  default cursor with an instance of SQLiteCursorWrapper. This automatically
  makes execute, executemany, executescript and others use the
  SQLiteCursorWrapper.
  """

  def cursor(self):
    """Substitutes standard cursor() with a SQLiteCursorWrapper to log queries.

    Substitutes the standard sqlite.Cursor with SQLiteCursorWrapper to ensure
    all cursor requests get intercepted.

    Returns a SQLiteCursorWrapper instance.
    """
    return super(SQLiteConnectionWrapper, self).cursor(SQLiteCursorWrapper)

class SQLiteDataStore(DataStore):
  """SQLite database interface wrapper."""

  def __init__(self, name=None, verbose=False, check_same_thread=True):
    DataStore.__init__(self, name or ":memory:")
    self._check_same_thread = check_same_thread
    if verbose:
      self._sql_conn = SQLiteConnectionWrapper
    else:
      self._sql_conn = sqlite3.Connection
    self._connection = None
    if check_same_thread:
      self._connection = self._connect()

  def _connect(self, settings={}):
    return sqlite3.connect(
      self._name,
      check_same_thread=self._check_same_thread,
      timeout=_MAX_TIMEOUT,
      factory=self._sql_conn,
      **settings
    )

  def get_connection(self, settings={}):
    """Returns Connection instance to SQLite database."""
    return self._connection and self._connection or self._connect(settings)

class SQLiteDataModel(DBDataModel):
  """This class represents data model based on SQLite DB."""

  def __init__(self, db_name=None, verbose=False):
    DBDataModel.__init__(self, SQLiteDataStore(db_name, verbose=verbose))

  def __del__(self):
    conn = self._data_store.get_connection()
    conn.commit()
    conn.close()

  def get_max_obj_value(self, name):
    conn = self._data_store.get_connection()
    result = conn.execute("SELECT MAX(value) FROM %s_solutions" % name)
    return result.fetchone()[0]

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
        % (tbl_name, ", ".join(tbl_cols),
           ", ".join(map(str, tbl_vals + [obj_value])),
           " + ".join(["MAX("+name + ".value)" for name in dep_tbls]),
           " ".join(deps))
    self._data_store.get_connection().execute(sql_stmt)
