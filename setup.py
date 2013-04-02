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

from __future__ import print_function

import os
from setuptools import setup, find_packages, Extension
import sys
import types

install_requires = [
  "networkx",
  "scipy",
  "numpy"
]

extensions = []

SYMPHONY_HOME_DIR = os.environ.get("SYMPHONY_HOME_DIR")
# Do we have METIS or we have to provide the support for it...
if os.environ.get("METIS_DLL"):
  install_requires.append("metis")

def setup_symphony(home_dir):
  """Setup SYMPHONY solver."""
  if not isinstance(home_dir, types.StringType):
    raise TypeError()
  if not os.path.exists(home_dir):
    raise IOError("Directory doesnot exist: %s" % home_dir)
  include_dir = os.path.join(home_dir, "include")
  lib_dir = os.path.join(home_dir, "lib")
  # Extensions
  extensions.append(
    Extension(
      "les.ext.coin.coin_utils",
      ["les/ext/coin/coin_utils.cc"],
      libraries=["boost_python", "CoinUtils"],
      include_dirs=[include_dir],
      library_dirs=[lib_dir]
    )
  )
  extensions.append(
    Extension(
      "les.ext.coin._osi_sym_solver_interface",
      ["les/ext/coin/osi_sym_solver_interface.cc"],
      define_macros=[("BOOST_PYTHON_NO_PY_SIGNATURES", 1)],
      libraries=["boost_python",
                 "OsiSym","Sym", "Cgl", "OsiClp", "Clp", "Osi", "CoinUtils"],
      include_dirs=[include_dir],
      library_dirs=[lib_dir]
    )
  )
  extensions.append(
    Extension(
      "les.ext.coin._osi_clp_solver_interface",
      ["les/ext/coin/osi_clp_solver_interface.cc"],
      define_macros=[("BOOST_PYTHON_NO_PY_SIGNATURES", 1)],
      libraries=["boost_python",
                 "OsiClp","Clp", "Cgl", "Osi", "CoinUtils"],
      include_dirs=[include_dir],
      library_dirs=[lib_dir]
    )
  )

def main():
  if SYMPHONY_HOME_DIR:
    setup_symphony(SYMPHONY_HOME_DIR)
  else:
    print("WARNING: SYMPHONY home dir wasn't set", file=sys.stderr)
  setup(
    name="les",
    description="Local Elimination Solver",
    author="Oleksandr Sviridenko",
    author_email="oleks.sviridenko@gmail.com",
    packages=find_packages(),
    test_suite="test.make_testsuite",
    ext_modules=extensions,
    license="Apache",
    classifiers=[
      "License :: OSI Approved :: Apache Software License",
      ],
    install_requires=install_requires
  )

if __name__ == "__main__":
  main()
