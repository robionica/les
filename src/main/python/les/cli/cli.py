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

import argparse
import inspect
import pkgutil
import re
import sys

from les.cli import commands
from les.cli.commands import command_base
from les.utils import logging

DEFAULT_LOGGING_LEVEL = "INFO"

EPILOG = ('Post bug reports and suggestions to ' +
          '<https://github.com/d2rk/les/issues>.')

def _camel_case_to_lower_case_underscore(s):
  '''Converts camer case to lower case underscore, e.g. "DrawDecompositionTree"
  to "draw_decomposition_tree".'''
  s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class CLI(object):
  '''This class represets command-line interface.

  By default :attr:`default_command` will be used as default command.
  '''

  default_command = 'optimize'

  def __init__(self):
    self._argparser = argparse.ArgumentParser(prog='les', epilog=EPILOG)
    self._argparser.add_argument('--logging-level', dest='logging_level', type=str,
                                 metavar='LEVEL', default=DEFAULT_LOGGING_LEVEL,
                                 help=('logging level for the messages such as DEBUG, '
                                 'INFO, WARNING, ERROR, CRITICAL (default: %s)'
                                 % DEFAULT_LOGGING_LEVEL))
    self._argsubparsers = None
    self._cmds = {}
    self._discover_commands()
    self._argparser.add_argument('file', metavar='FILE', type=str)

  def _discover_commands(self):
    for _, mod, is_pkg in pkgutil.iter_modules(commands.__path__):
      if is_pkg:
        continue
      fq_module = '.'.join([commands.__name__, mod])
      try:
        __import__(fq_module)
      except ImportError, e:
        self.exit_and_fail(e)
      for (_, cls) in inspect.getmembers(sys.modules[fq_module],
                                         inspect.isclass):
        if (issubclass(cls, command_base.CommandBase) and
            not cls is command_base.CommandBase):
          self.add_command_class(cls)

  def add_command_class(self, cls):
    '''Registers new command class. The command name will be equal to the class
    name converted from camel case to underscore case. The command will have own
    argument parser instance that it has to setup.
    '''
    if not self._argsubparsers:
      self._argsubparsers = self._argparser.add_subparsers(help='command help')
    name = _camel_case_to_lower_case_underscore(cls.__name__)
    argparser = self._argsubparsers.add_parser(name)
    cls.setup_argparser(argparser)
    argparser.set_defaults(_command_class=cls)
    self._cmds[name] = cls

  def exit_and_fail(self, message):
    print message
    exit(0)

  def run(self, argv=sys.argv):
    self._args = self._argparser.parse_args(argv[1:])
    logger = logging.get_logger()
    self._args.logging_level = self._args.logging_level.upper()
    if not self._args.logging_level in ("DEBUG", "INFO", "WARNING", "ERROR",
                                        "CRITICAL"):
      self.exit_and_fail("Unknown logging level: %s" % self._args.logging_level)
    logger.setLevel(getattr(logging, self._args.logging_level))
    result = 0
    try:
      cmd_cls = self._args._command_class
      cmd = cmd_cls(args=self._args)
      result = cmd.run()
    except KeyboardInterrupt:
      cmd.cleanup()
    return result

  def get_commands_names(self):
    '''Returns a copy of list with all commands names.'''
    return self._cmds.keys()
