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
#include <coin/CoinPackedMatrix.hpp>

#include <boost/python.hpp>

using namespace boost::python;

struct CoinPackedMatrixWrap : CoinPackedMatrix, wrapper<CoinPackedMatrix> {
public:
  CoinPackedMatrixWrap() : CoinPackedMatrix() {}

  void appendRow1(const CoinPackedVectorBase& vec) {
    CoinPackedMatrix::appendRow(vec);
  }

  void appendCol1(const CoinPackedVectorBase& vec) {
    CoinPackedMatrix::appendCol(vec);
  }
};

BOOST_PYTHON_MODULE(coin_utils)
{
  // Overriding virtual functions:
  // http://wiki.python.org/moin/boost.python/OverridableVirtualFunctions
  class_<CoinPackedVectorBase, boost::noncopyable,
         boost::shared_ptr<CoinPackedVector> >("CoinPackedVector")
    .def("insert", &CoinPackedVector::insert)
    ;

  class_<CoinPackedMatrixWrap, boost::noncopyable>("CoinPackedMatrix")
    // Query members
    .def("get_num_rows", &CoinPackedMatrixWrap::getNumRows)
    .def("get_num_cols", &CoinPackedMatrixWrap::getNumCols)
    .def("get_size_vector_lengths", &CoinPackedMatrixWrap::getSizeVectorLengths)
    // Modifying members
    .def("append_row", &CoinPackedMatrixWrap::appendRow1)
    .def("append_col", &CoinPackedMatrixWrap::appendCol1)
    ;
}
