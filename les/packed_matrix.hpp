// Copyright (c) 2012 Alexander Sviridenko
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied.  See the License for the specific language governing
// permissions and limitations under the License.
//
// Packed matrix.

#ifndef __LES_PACKED_MATRIX_HPP
#define __LES_PACKED_MATRIX_HPP

#include <stdio.h>
#include <map>
#include <vector>

#include "les/config.hpp"
#include "les/packed_vector.hpp"

// TODO: the current implementation is completely depends on COIN package. This
// has to be fixed.
#define USE_PACKED_MATRIX_COINOR_WRAPPER

// The following PackedMatrix implementation is a wrapper for CoinPackedMatrix
// class and thus depends on from COIN-OR project. However it designed to
// support the API for the future independent version.
#ifdef USE_PACKED_MATRIX_COINOR_WRAPPER

#include <coin/CoinPackedMatrix.hpp>
#include <coin/CoinShallowPackedVector.hpp>

// TODO: CoinPackedMatrix doesn't provide *good* sparsity, thus do we need to
// provide col delta and row delta in order to *compres* it? We can use the
// following API fix_col_index() and fix_row_index() to fix cols and rows.
class PackedMatrix {
public:
  // Default constructor creates an empty column ordered packed matrix.
  PackedMatrix() {
    // By default we need column ordered matrix.
    slave_matrix_.reverseOrdering();
  }

  inline int get_num_elements() const {
    return slave_matrix_.getNumElements();
  }

  inline const double* get_elements() const {
    return slave_matrix_.getElements();
  }

  // Return vector of indices. Use get_num_elements() to get length
  // of this vector.
  inline const int* get_indices() const {
    return slave_matrix_.getIndices();
  }

  // Return number of cols. Note it doesn't return the actual number
  // of nonzero cols (see get_num_elements()). Use get_num_nonzero_cols().
  inline int get_num_cols() const {
    return slave_matrix_.getNumCols();
  }

  // Returns vector of nonzero columns. Note, once it has been use, you
  // need to free() it.
  vector<int>* get_nonzero_cols() const;

  // Returns vector of nonzero rows.
  vector<int>* get_nonzero_rows() const;

  // Counts and returns number of nonzero columns. See
  // get_nonzero_cols().
  inline int get_num_nonzero_cols() const {
    vector<int>* nonzero_cols;
    nonzero_cols = get_nonzero_cols();
    int sz = nonzero_cols->size();
    delete nonzero_cols;
    return sz;
  }

  // Dumps matrix content.
  inline void dump() const {
    slave_matrix_.dumpMatrix();
  }

  inline int get_num_rows() const {
    return slave_matrix_.getNumRows();
  }

  // If autoresize is enabled and col or row doesn't exist, the matrix
  // will be resized.
  inline void set_coefficient(int i, int j, double v,
                              bool autoresize=true) {
    if (autoresize) {
      int nr = ((i + 1) > get_num_rows()) ? (i + 1) : -1;
      int nc = ((j + 1) > get_num_cols()) ? (j + 1) : -1;
      if (nr || nc) {
        resize(nr, nc);
      }
    }
    slave_matrix_.modifyCoefficient(i, j, v);
  }

  // Returns one element of the matrix. Return 0.0 if element doesn't
  // present.
  inline double get_coefficient(int i, int j) {
    return slave_matrix_.getCoefficient(i, j);
  }

  // Just an alias for get_coefficient() method.
  inline double get_coef(int i, int j) {
    return get_coefficient(i, j);
  }

  // Returns the length of i'th vector.
  inline int get_vector_size(int i) const {
    return slave_matrix_.getVectorLengths()[i];
  }

  // Resize the matrix. Mark dimension as -1 to live it as it is.
  inline void resize(int i, int j) {
    slave_matrix_.setDimensions(i, j);
  }

  // Just an alias for get_vector().
  inline PackedVector* get_row(int i) const {
    return get_vector(i);
  }

  // Returns i'th PackedVector vector. Converts CoinPackedVector to
  // PackedVector.
  PackedVector* get_vector(int i) const;

  // Default destructor.
  ~PackedMatrix() {
  }

  protected:
  // Slave matrix that will be handled by particular class.
  CoinPackedMatrix slave_matrix_;
};
#endif /* USE_PACKED_MATRIX_COINOR_WRAPPER */

#endif /* __LES_PACKED_MATRIX_HPP */
