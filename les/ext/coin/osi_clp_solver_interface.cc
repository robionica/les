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
#include <coin/OsiSolverInterface.hpp>
#include <coin/OsiClpSolverInterface.hpp>

#include <boost/python.hpp>

using namespace boost::python;

struct OsiClpSolverInterfaceWrap : OsiClpSolverInterface,
                                   wrapper<OsiClpSolverInterface> {
public:
  OsiClpSolverInterfaceWrap() : OsiClpSolverInterface() {}

  virtual void addCol(const CoinPackedVector& vec, const double collb,
                      const double colub, const double obj) {
    OsiClpSolverInterface::addCol(vec, collb, colub, obj);
  }

  virtual void addRow(const CoinPackedVectorBase& vec,
                      const char rowsen, const double rowrhs,
                      const double rowrng) {
    OsiClpSolverInterface::addRow(vec, rowsen, rowrhs, rowrng);
  }

  virtual boost::python::object default_getColSolution() const {
    const double* solution = OsiClpSolverInterface::getColSolution();
    boost::python::list lst;
    for (int i = 0; i < OsiClpSolverInterface::getNumCols(); i++) {
      lst.append(solution[i]);
    }
    return lst;
  }
};

BOOST_PYTHON_MODULE(osi_clp_solver_interface)
{
  class_<OsiClpSolverInterfaceWrap, bases<OsiSolverInterface>,
         boost::noncopyable>("OsiClpSolverInterface")
    // Solve methods
    .def("branch_and_bound", &OsiClpSolverInterfaceWrap::branchAndBound)
    .def("initial_solve", &OsiClpSolverInterfaceWrap::initialSolve)
    .def("resolve", &OsiClpSolverInterfaceWrap::resolve)
    // Methods to expand a problem
    .def("add_col", &OsiClpSolverInterfaceWrap::addCol)
    .def("add_row", &OsiClpSolverInterfaceWrap::addRow)
    // Problem query methods
    .def("get_num_cols", &OsiClpSolverInterfaceWrap::getNumCols)
    .def("get_num_rows", &OsiClpSolverInterfaceWrap::getNumRows)
    .def("get_num_elements", &OsiClpSolverInterfaceWrap::getNumElements)
    .def("get_obj_sense", &OsiClpSolverInterfaceWrap::getObjSense)
    .def("get_infinity", &OsiClpSolverInterfaceWrap::getInfinity)
    // Solution query methods
    .def("get_col_solution", &OsiClpSolverInterfaceWrap::default_getColSolution)
    .def("get_obj_value", &OsiClpSolverInterfaceWrap::getObjValue)
    // Methods to modify the objective, bounds, and solution
    .def("set_obj_sense", &OsiClpSolverInterfaceWrap::setObjSense)
    .def("set_row_upper", &OsiClpSolverInterfaceWrap::setRowUpper)
    // Message handling (extra for Clp messages)
    .def("set_log_level", &OsiClpSolverInterfaceWrap::setLogLevel)
    ;
}
