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
                                   wrapper<OsiSymSolverInterface> {
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

BOOST_PYTHON_MODULE(_osi_sym_solver_interface)
{
  class_<OsiSymSolverInterfaceWrap, boost::noncopyable>("OsiSymSolverInterface")
    // Solve methods
    .def("branch_and_bound", &OsiSymSolverInterfaceWrap::branchAndBound)
    .def("initial_solve", &OsiSymSolverInterfaceWrap::initialSolve)
    .def("resolve", &OsiSymSolverInterfaceWrap::resolve)
    .def("multi_criteria_branch_and_bound",
         &OsiSymSolverInterfaceWrap::multiCriteriaBranchAndBound)
    // Methods returning info on how the solution process terminated
    .def("is_abandoned", &OsiSymSolverInterfaceWrap::isAbandoned)
    .def("is_proven_optimal", &OsiSymSolverInterfaceWrap::isProvenOptimal)
    .def("is_proven_primal_infeasible",
         &OsiSymSolverInterfaceWrap::isProvenPrimalInfeasible)
    .def("is_proven_dual_infeasible",
         &OsiSymSolverInterfaceWrap::isProvenDualInfeasible)
    .def("is_iteration_limit_reached",
         &OsiSymSolverInterfaceWrap::isIterationLimitReached)
    .def("is_time_limit_reached", &OsiSymSolverInterfaceWrap::isTimeLimitReached)
    .def("is_target_gap_reached", &OsiSymSolverInterfaceWrap::isTargetGapReached)
    // Methods to expand a problem
    .def("add_col", &OsiSymSolverInterfaceWrap::addCol)
    .def("add_row", &OsiSymSolverInterfaceWrap::addRow)
    // Problem query methods
    .def("get_num_cols", &OsiSymSolverInterfaceWrap::getNumCols)
    .def("get_num_rows", &OsiSymSolverInterfaceWrap::getNumRows)
    .def("get_num_elements", &OsiSymSolverInterfaceWrap::getNumElements)
    .def("get_obj_sense", &OsiSymSolverInterfaceWrap::getObjSense)
    .def("get_infinity", &OsiSymSolverInterfaceWrap::getInfinity)
    // Methods to set variable type
    .def("set_integer", &OsiSymSolverInterfaceWrap::setInteger)
    // Solution query methods
    .def("get_col_solution", &OsiSymSolverInterfaceWrap::default_getColSolution)
    .def("get_obj_value", &OsiSymSolverInterfaceWrap::getObjValue)
    // Methods to modify the objective, bounds, and solution
    .def("set_obj_sense", &OsiSymSolverInterfaceWrap::setObjSense)
    // Parameter set/get methods
    .def("set_sym_param", &OsiSymSolverInterfaceWrap::setSymParam)
    ;
}
