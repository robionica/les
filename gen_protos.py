#!/usr/bin/env python
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

import distutils.spawn
import distutils.log
import os.path
import subprocess
import sys

PYTHON_SRC_DIR = os.path.join('src', 'main', 'python')
PROTOBUF_SRC_DIR = os.path.join('src', 'main', 'protobuf')
PROTOC = distutils.spawn.find_executable('protoc')

def gen_proto(in_file):
  '''Invokes the Protocol Compiler to generate a _pb2.py from the given .proto
  file. Does nothing if the output already exists and is newer than the input.
  '''
  if not isinstance(in_file, str):
    raise TypeError('in_file must be a string: %s' % type(in_file))
  out_file = in_file.replace('.proto', '_pb2.py').replace(PROTOBUF_SRC_DIR,
                                                            PYTHON_SRC_DIR)
  out_dir = os.path.dirname(out_file)
  if not os.path.exists(in_file):
    distutils.log.error('Cannot find required file: %s', in_file)
    sys.exit(-1)
  distutils.log.info('Generating %s...', out_file)
  if (not os.path.exists(out_file) or
      (os.path.exists(in_file) and
       os.path.getmtime(in_file) > os.path.getmtime(out_file))):
    if PROTOC == None:
      distutils.log.error('protoc is not installed nor found in %s. '
                          'Please compile it or install the binary package.\n',
                          PROTOBUF_SRC_DIR)
      sys.exit(-1)
    protoc_command = [PROTOC, '-I' + PROTOBUF_SRC_DIR, '-I.',
                      '--python_out=' + PYTHON_SRC_DIR, in_file]
    distutils.log.info('Executing... %s', ' '.join(protoc_command))
    if subprocess.call(protoc_command) != 0:
      sys.exit(-1)
  else:
    distutils.log.info('%s is up to date.', out_file)

def main():
  gen_proto(os.path.join(PROTOBUF_SRC_DIR, 'les', 'mp_model', 'mp_model.proto'))
  gen_proto(os.path.join(PROTOBUF_SRC_DIR, 'les', 'frontend_solver.proto'))

if __name__ == '__main__':
  distutils.log.set_verbosity(distutils.log.DEBUG)
  sys.exit(main())
