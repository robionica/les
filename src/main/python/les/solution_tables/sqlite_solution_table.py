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

import json
try:
  from pysqlite2 import dbapi2 as sqlite3
except ImportError:
  import sqlite3
import threading
import types
import sys

from les.mp_model import mp_solution
from les.solution_tables import db_solution_table_base
from les.utils import logging
from les.graphs import decomposition_tree

_MAX_TIMEOUT = 5.0

# The columns represent shared variables, while the key columns also include
# shared variables. true_vars constains a list of true variables.
_MODEL_SCHEMA_TEMPLATE = '''
DROP TABLE IF EXISTS {table_name};
CREATE TABLE {table_name}(
  {columns},
  value DOUBLE default 0.0,
  true_vars TEXT,
  PRIMARY KEY ({key_columns})
);
'''
_INDEX_TEMPLATE = 'CREATE INDEX IF NOT EXISTS {index} ON {name}({shared_vars});'
_INSERT_TEMPLATE = ('INSERT OR REPLACE INTO {table_name}({vars_names}, value, true_vars)'
                    ' VALUES({fields_values})')

class Error(Exception):
  pass

class SQLiteCursorWrapper(sqlite3.Cursor):
  '''Substitutes :class:`sqlite3.Cursor`, with a cursor that logs commands.

  Inherits from :class:`sqlite3.Cursor` class and extends methods such as
  execute, executemany and execute script, so it logs SQL calls.
  '''

  def execute(self, sql, *args):
    '''Replaces :func:`execute` with a logging variant.'''
    if args:
      parameters = []
      for arg in args:
        if isinstance(arg, buffer):
          parameters.append('<blob>')
        else:
          parameters.append(repr(arg))
      logging.debug('SQL Execute: %s - \n %s', sql,
                    '\n '.join(str(param) for param in parameters))
    else:
      logging.debug(sql)
    return super(SQLiteCursorWrapper, self).execute(sql, *args)

  def executemany(self, sql, seq_parameters):
    '''Replaces executemany() with a logging variant.'''
    seq_params_list = list(seq_parameters)
    logging.debug('SQL ExecuteMany: %s - \n %s', sql,
                  '\n '.join(str(param) for param in seq_params_list))
    return super(SQLiteCursorWrapper, self).executemany(sql, seq_params_list)

  def executescript(self, sql):
    '''Replaces :func:`executescript` with a logging variant.'''
    logging.debug('SQL ExecuteScript: %s', sql)
    return super(SQLiteCursorWrapper, self).executescript(sql)

class SQLiteConnectionWrapper(sqlite3.Connection):
  '''Substitutes :class:`sqlite3.Connection` with a connection that logs
  commands.

  Inherits from :class:`sqlite3.Connection` class and overrides cursor replacing
  the default cursor with an instance of :class:`SQLiteCursorWrapper`. This
  automatically makes execute, executemany, executescript and others use the
  :class:`SQLiteCursorWrapper`.
  '''

  def cursor(self):
    '''Substitutes standard :func:`cursor` with a SQLiteCursorWrapper to log
    queries.

    Substitutes the standard :class:`sqlite.Cursor` with
    :class:`SQLiteCursorWrapper` to ensure all cursor requests get intercepted.

    Returns a :class:`SQLiteCursorWrapper` instance.
    '''
    return super(SQLiteConnectionWrapper, self).cursor(SQLiteCursorWrapper)

class SQLiteDataStore(db_solution_table_base.DataStore):
  '''SQLite database interface wrapper.

  :param name: data base name. Set as ':memory:' to keep data in memory.
  '''

  def __init__(self, name=None, verbose=False):
    db_solution_table_base.DataStore.__init__(self, name or ':memory:')
    if verbose:
      self._sql_conn = SQLiteConnectionWrapper
    else:
      self._sql_conn = sqlite3.Connection
    self._connection = sqlite3.connect(self.get_name(), check_same_thread=False,
                                       timeout=_MAX_TIMEOUT,
                                       factory=self._sql_conn)
    self.__connection_lock = threading.RLock()

  def get_connection(self):
    '''Returns :class:`Connection` instance to SQLite database.'''
    self.__connection_lock.acquire()
    return self._connection

  def release_connection(self, conn):
    '''Releases a connection for use by other operations.

    If a transaction is supplied, no action is taken.
    '''
    conn.commit()
    self.__connection_lock.release()

class SQLiteSolutionTable(db_solution_table_base.DBSolutionTableBase):
  '''This class represents solution table based on SQLite database. Helps to
  store solutions in an SQLite database.

  :param verbose: Be verbose?
  '''

  def __init__(self, db_name=None, verbose=False):
    db_solution_table_base.DBSolutionTableBase.__init__(
      self, SQLiteDataStore(db_name, verbose=verbose))
    self._decomposition_tree = None

  def __del__(self):
    conn = self.get_data_store().get_connection()
    conn.commit()
    conn.close()

  def get_solution(self):
    if not self._decomposition_tree:
      raise Error("decomposition_tree wasn't set")
    conn = self._data_store.get_connection()
    result = conn.execute('SELECT MAX(value), true_vars FROM %s' %
                          self._decomposition_tree.get_root())
    try:
      objective_value, true_vars = result.fetchone()
    except Exception:
      raise Error()
    solution = mp_solution.MPSolution()
    solution.set_objective_value(objective_value)
    true_vars = json.loads(true_vars)
    solution.set_variables_values(true_vars, [1.0] * len(true_vars))
    return solution

  def set_decomposition_tree(self, tree):
    if not isinstance(tree, decomposition_tree.DecompositionTree):
      raise TypeError()
    self._decomposition_tree = tree
    for model in tree.get_models():
      node = tree.node[model.get_name()]
      sql_script = _MODEL_SCHEMA_TEMPLATE.format(
        table_name=model.get_name(),
        columns=','.join(['%s INTEGER DEFAULT NULL' % name for name in
                          node.get_shared_variables()]),
        key_columns=','.join(node.get_shared_variables())
      )
      for dep_node in tree.predecessors(node.get_name()):
        edge = tree.get_edge_between(dep_node, node.get_name())
        shared_vars = edge.get_shared_variables()
        sql_script += _INDEX_TEMPLATE.format(
          index='_'.join(shared_vars) + '_index',
          name=model.get_name(),
          shared_vars=', '.join(shared_vars))
      try:
        conn = self.get_data_store().get_connection()
        conn.executescript(sql_script)
        self.get_data_store().release_connection(conn)
      except sqlite3.OperationalError, e:
        logging.warning('SQLite script %s: %s' % (sql_script, e))
        raise Error()

  def dump(self, stream=sys.stdout):
    '''Dumps all existed solution tables for all processed models.'''
    if not self._decomposition_tree:
      raise Error()
    conn = self.get_data_store().get_connection()
    for model in self._decomposition_tree.get_models():
      stream.write('TABLE %s\n' % model.get_name())
      cur = conn.execute('SELECT * FROM ' + model.get_name())
      for field_descr in cur.description:
        stream.write(field_descr[0].ljust(6))
      stream.write('\n')
      # For each row, print the value of each field left-justified within
      # the maximum possible width of that field.
      field_indices = range(len(cur.description))
      for row in cur:
        for field_index in field_indices:
          field_value = str(row[field_index])
          stream.write(field_value.ljust(6))
        stream.write('\n')
      stream.write('\n')
    self.get_data_store().release_connection(conn)

  def write_solution(self, model, solution):
    stmt = []
    d = 0
    for name in self._decomposition_tree.neighbors(model.get_name()):
      edge = self._decomposition_tree.get_edge_between(model.get_name(), name)
      for i in edge.get_shared_variables():
        if solution.get_variable_value_by_name(i) == 1.0:
          ii = model.get_columns_names().index(i)
          d += model.get_objective_coefficients()[ii]
      stmt += [''.join(['SELECT MAX(', name, '.value), ', name, '.true_vars'])]
      stmt += [' '.join(['FROM', name, 'WHERE'])]
      stmt += [' AND '.join(['%s.%s=%d' % (name, i, solution.get_variable_value_by_name(i)) for i in edge.get_shared_variables()])]
    dep_true_vars = ''
    if stmt:
      solution.set_objective_value(solution.get_objective_value() + d)
      conn = self.get_data_store().get_connection()
      res = conn.execute(' '.join(stmt))
      # TODO(d2rk): sometimes there is no dependencies. I guess this happens
      # when some solutions are not satisfing constrains. We need to check this
      # more carefully.
      dep_value, dep_true_vars = res.fetchone()
      solution.set_objective_value(solution.get_objective_value()
                                   + (dep_value or 0.0))

    indices = xrange(len(solution.get_variables_names()))
    if not indices:
      return
    node = self._decomposition_tree.node[model.get_name()]
    _true_vars = ([solution.get_variables_names()[i]
                   for i in solution.get_variables_values().get_entries_indices()] +
                  (dep_true_vars and json.loads(dep_true_vars) or []))
    true_vars = json.dumps(list(set(_true_vars)))
    stmt = _INSERT_TEMPLATE.format(
      table_name=model.get_name(),
      vars_names=', '.join(node.get_shared_variables()),
      fields_values=', '.join(['?'] * (len(node.get_shared_variables()) + 2))
    )
    conn = self.get_data_store().get_connection()
    conn.execute(stmt, [solution.get_variable_value_by_name(i) for i in
                        node.get_shared_variables()] +
                 [float(solution.get_objective_value())] + [true_vars])
    self.get_data_store().release_connection(conn)
