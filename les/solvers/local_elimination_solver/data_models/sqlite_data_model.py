#!/usr/bin/env python
#
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
import threading
import types

from les.solvers.local_elimination_solver.data_models.db_data_model import DBDataModel, DataStore

_MAX_TIMEOUT = 5.0

_SUBPROBLEM_SCHEMA = """
DROP TABLE IF EXISTS %(name)s;
CREATE TABLE %(name)s(
  %(cols)s,
  value DOUBLE default 0.0,
  signed_cols TEXT,
  PRIMARY KEY (%(key)s)
);
"""

class SQLiteCursorWrapper(sqlite3.Cursor):
  """Substitutes :class:`sqlite3.Cursor`, with a cursor that logs commands.

  Inherits from :class:`sqlite3.Cursor` class and extends methods such as
  execute, executemany and execute script, so it logs SQL calls.
  """

  logger = logging.getLogger()

  def execute(self, sql, *args):
    """Replaces :func:`execute` with a logging variant."""
    if args:
      parameters = []
      for arg in args:
        if isinstance(arg, buffer):
          parameters.append('<blob>')
        else:
          parameters.append(repr(arg))
      self.logger.debug('SQL Execute: %s - \n %s', sql,
                   '\n '.join(str(param) for param in parameters))
    else:
      self.logger.debug(sql)
    return super(SQLiteCursorWrapper, self).execute(sql, *args)

  def executemany(self, sql, seq_parameters):
    """Replaces executemany() with a logging variant."""
    seq_parameters_list = list(seq_parameters)
    self.logger.debug('SQL ExecuteMany: %s - \n %s', sql,
                      '\n '.join(str(param) for param in seq_parameters_list))
    return super(SQLiteCursorWrapper, self).executemany(sql,
                                                        seq_parameters_list)

  def executescript(self, sql):
    """Replaces :func:`executescript` with a logging variant."""
    self.logger.debug('SQL ExecuteScript: %s', sql)
    return super(SQLiteCursorWrapper, self).executescript(sql)

class SQLiteConnectionWrapper(sqlite3.Connection):
  """Substitutes :class:`sqlite3.Connection` with a connection that logs
  commands.

  Inherits from :class:`sqlite3.Connection` class and overrides cursor replacing
  the default cursor with an instance of :class:`SQLiteCursorWrapper`. This
  automatically makes execute, executemany, executescript and others use the
  :class:`SQLiteCursorWrapper`.
  """

  def cursor(self):
    """Substitutes standard :func:`cursor` with a SQLiteCursorWrapper to log
    queries.

    Substitutes the standard :class:`sqlite.Cursor` with
    :class:`SQLiteCursorWrapper` to ensure all cursor requests get intercepted.

    Returns a :class:`SQLiteCursorWrapper` instance.
    """
    return super(SQLiteConnectionWrapper, self).cursor(SQLiteCursorWrapper)

class SQLiteDataStore(DataStore):
  """SQLite database interface wrapper."""

  def __init__(self, name=None, verbose=False):
    DataStore.__init__(self, name or ":memory:")
    if verbose:
      self._sql_conn = SQLiteConnectionWrapper
    else:
      self._sql_conn = sqlite3.Connection
    self._connection = sqlite3.connect(
      self._name,
      check_same_thread=False,
      timeout=_MAX_TIMEOUT,
      factory=self._sql_conn
    )
    self.__connection_lock = threading.RLock()

  def get_connection(self):
    """Returns :class:`Connection` instance to SQLite database."""
    self.__connection_lock.acquire()
    return self._connection

  def release_connection(self, conn):
    """Releases a connection for use by other operations.

    If a transaction is supplied, no action is taken.
    """
    conn.commit()
    self.__connection_lock.release()

class SQLiteDataModel(DBDataModel):
  """This class represents data model based on SQLite database. Helps to store
  problem data in an SQLite database.
  """

  def __init__(self, db_name=None, verbose=False):
    DBDataModel.__init__(self, SQLiteDataStore(db_name, verbose=verbose))
    self._subproblems = None

  def __del__(self):
    conn = self.get_data_store().get_connection()
    conn.commit()
    conn.close()

  def get_solution(self, name):
    conn = self._data_store.get_connection()
    result = conn.execute("SELECT MAX(value), signed_cols FROM %s" % name)
    return result.fetchone()

  def _configure_subproblem(self, problem):
    def join_cols(joiner, cols, frmt="x%d"):
      return joiner.join([frmt % i for i in cols])
    # Create table
    sql_script = _SUBPROBLEM_SCHEMA % {
      'name': problem.get_name(),
      'cols': ', '.join(map(lambda i: "x%d INTEGER DEFAULT NULL" % i,
                            problem.get_nonzero_cols())),
      'key': join_cols(", ", problem.get_shared_cols())
    }
    # Create indices
    for another_subproblem, cols in problem.get_dependencies().items():
      sql_script += "CREATE INDEX IF NOT EXISTS %s_index ON %s(%s);\n" \
          % (join_cols("_", cols), problem.get_name(), join_cols(", ", cols))
    try:
      conn = self.get_data_store().get_connection()
      conn.executescript(sql_script)
      self.get_data_store().release_connection(conn)
    except sqlite3.OperationalError, e:
      print e
      print "SQLite script:", sql_script
      raise Exception()

  def configure(self, subproblems):
    """Configures data model, creates tables for each subproblem."""
    for subproblem in subproblems:
      self._configure_subproblem(subproblem)
    self._subproblems = subproblems

  def process(self, problem):
    if not problem.get_dependencies():
      return
    conn = self.get_data_store().get_connection()
    try:
      cursor = conn.execute("SELECT * FROM %s" % problem.get_name())
      cols = list(map(lambda x: x[0], cursor.description))
      for row in cursor:
        m = dict(zip(cols, row))
        obj_value = m["value"]
        del m["value"]
        signed_cols = m["signed_cols"] or None
        del m["signed_cols"]
        dep_tbls = []
        deps = []
        for dep_problem, dep_cols in problem.get_dependencies().items():
          where = []
          dep_tbls.append(dep_problem.get_name())
          for i in dep_cols:
            where.append("%s.x%d=%d" % (dep_problem.get_name(), i, m["x%d" % i]))
          deps.append("FROM %s WHERE %s" % (dep_problem.get_name(), " AND ".join(where)))
        stmt = "%s %s" \
            % (
               " + ".join(["SELECT MAX("+name + ".value), "+name+".signed_cols" for name in dep_tbls]),
               " ".join(deps)
               )
        res = conn.execute(stmt)
        # NOTE: sometimes there is no dependencies. I guess this happens when
        # some solutions are not satisfing constrains. We need to check this
        # more carefully.
        dep_value, dep_signed_cols = res.fetchone()
        if dep_value:
          obj_value += dep_value
        signed_cols = ','.join(filter(None, [signed_cols, dep_signed_cols]))
        stmt = "UPDATE %s SET value = %f, signed_cols = '%s' WHERE %s" \
            % (problem.get_name(), obj_value, signed_cols,
               " AND ".join(["%s=%d" % (c, v) for c, v in m.items()]))
        conn.execute(stmt)
    finally:
      self.get_data_store().release_connection(conn)

  def put(self, problem, col_solution, obj_value):
    cols = []
    vals = []
    signed_cols = []
    for i in list(problem.get_nonzero_cols()):
      cols.append("x%d" % i)
      v = int(col_solution[i])
      vals.append(v)
      if v:
        signed_cols.append(str(i))
    stmt = "INSERT INTO %s(%s, value, signed_cols) VALUES(%s)" \
        % (problem.get_name(), ", ".join(cols), ", ".join(["?"] * (len(cols)+2)))
    conn = self.get_data_store().get_connection()
    conn.execute(stmt, vals + [float(obj_value)] + [','.join(signed_cols)])
    self.get_data_store().release_connection(conn)
