// -*- coding: utf-8; mode: c++; -*-
//
// Copyright (c) 2013 Oleksandr Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <coin/CoinPackedVector.hpp>
#include <coin/OsiSymSolverInterface.hpp>

#include <boost/python.hpp>

using namespace boost::python;

struct OsiSymSolverInterfaceWrap : OsiSymSolverInterface,
                                   wrapper<OsiSymSolverInterface>
{
public:
  OsiSymSolverInterfaceWrap() : OsiSymSolverInterface() {}

  virtual void addCol(const CoinPackedVector& vec, const double collb,
                      const double colub, const double obj) {
    OsiSymSolverInterface::addCol(vec, collb, colub, obj);
  }

  virtual void addRow(const CoinPackedVectorBase& vec,
                      const char rowsen, const double rowrhs,
                      const double rowrng) {
    OsiSymSolverInterface::addRow(vec, rowsen, rowrhs, rowrng);
  }

  virtual void setInteger(int i) {
    OsiSymSolverInterface::setInteger(i);
  }

  virtual bool setSymParam(const std::string key, int value) {
    return OsiSymSolverInterface::setSymParam(key, value);
  }

  virtual boost::python::object default_getColSolution() const {
    const double* solution = OsiSymSolverInterface::getColSolution();
    boost::python::list lst;
    for (int i = 0; i < OsiSymSolverInterface::getNumCols(); i++) {
      lst.append(solution[i]);
    }
    return lst;
  }
};

BOOST_PYTHON_MODULE(osi_sym_solver_interface)
{
  class_<OsiSymSolverInterfaceWrap, boost::noncopyable>("OsiSymSolverInterface")
    .def("add_col", &OsiSymSolverInterfaceWrap::addCol)
    .def("add_row", &OsiSymSolverInterfaceWrap::addRow)
    .def("branch_and_bound", &OsiSymSolverInterfaceWrap::branchAndBound)
    .def("set_integer", &OsiSymSolverInterfaceWrap::setInteger)
    .def("get_col_solution", &OsiSymSolverInterfaceWrap::default_getColSolution)
    .def("set_obj_sense", &OsiSymSolverInterfaceWrap::setObjSense)
    .def("get_num_cols", &OsiSymSolverInterfaceWrap::getNumCols)
    .def("get_num_rows", &OsiSymSolverInterfaceWrap::getNumRows)
    .def("get_obj_value", &OsiSymSolverInterfaceWrap::getObjValue)
    .def("set_sym_param", &OsiSymSolverInterfaceWrap::setSymParam)
    ;
}
