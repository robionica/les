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

'''MPS (Mathematical Programming System) is a file format for presenting and
archiving linear programming (LP) and mixed integer programming problems.

Read more about format specs:

* <http://en.wikipedia.org/wiki/MPS_(format)>
* <http://lpsolve.sourceforge.net/5.5/mps-format.htm>
* <http://www.gurobi.com/documentation/5.5/reference-manual/node900>
'''

from les.mp_model.mp_model_builder.formats.mps.encoder import Encoder
from les.mp_model.mp_model_builder.formats.mps.decoder import Decoder

def decode(filename_or_stream):
  return Decoder(filename_or_stream)

def encode(filename_or_stream, data):
  return Encoder(filename_or_stream, data)
