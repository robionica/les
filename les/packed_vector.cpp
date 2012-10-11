/*
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <cstdlib>
#include <assert.h>
#include <string>
#include <iostream>
#include <vector>

#include <coin/CoinHelperFunctions.hpp>

#include "packed_vector.hpp"

#define max(a, b) ((a) > (b)) ? (a) : (b)

using namespace std;

PackedVector::PackedVector()
{
  indices_ = NULL;
  elements_ = NULL;
  nr_elements_ = 0;
  orig_indices_ = NULL;
  capacity_ = 0;
}

double
PackedVector::get_element_by_index(int i)
{
  map<int, int>::iterator it;
  it = index_to_pos_mapping_.find(i);
  if (it == index_to_pos_mapping_.end()) {
    return 0.0;
  }
  return get_element_by_pos(it->second);
}

void
PackedVector::clear()
{
  nr_elements_ = 0;
}

void
PackedVector::zero()
{
  for (int i = 0; i < get_num_elements(); i++) {
    elements_[i] = 0.0;
  }
}

void
PackedVector::resize(size_t n)
{
  reserve(n);
}

void
PackedVector::init(size_t size, const int* indices,
                   const double* elements)
{
  clear();
  if (size > 0) {
    reserve(size);
    nr_elements_ = size;
    CoinDisjointCopyN(indices, size, indices_);
    if (elements != NULL) {
      CoinDisjointCopyN(elements, size, elements_);
    } else {
      zero();
    }
    CoinIotaN(orig_indices_, size, 0);
    index_to_pos_mapping_.clear();
    for (size_t i = 0; i < size; i++) {
      index_to_pos_mapping_[indices[i]] = i;
    }
  }
}

void
PackedVector::init(vector<int>& indices)
{
  init(indices.size(), &indices[0], NULL);
}

void
PackedVector::init(vector<int>& indices, vector<double>& elements)
{
  init(indices.size(), &indices[0], &elements[0]);
}

void
PackedVector::insert(int index, double element)
{
  if(capacity_ <= get_num_elements()) {
    reserve(max(5, 2 * capacity_));
    assert(capacity_ > get_num_elements());
  }
  indices_[get_num_elements()] = index;
  index_to_pos_mapping_[index] = get_num_elements();
  elements_[get_num_elements()] = element;
  orig_indices_[get_num_elements()] = get_num_elements();
  nr_elements_++;
}

void
PackedVector::reserve(int n)
{
  /* Don't make allocated space smaller */
  if (n <= capacity_) {
    return;
  }
  capacity_ = n;
  /* Save pointers to existing data */
  int* temp_indices = indices_;
  int* temp_orig_indices = orig_indices_;
  double* temp_elements = elements_;
  /* Allocate new space */
  indices_ = (int*) calloc(capacity_, sizeof(int));
  orig_indices_ = (int*) calloc(capacity_, sizeof(int));
  elements_ = (double*) calloc(capacity_, sizeof(double));
  /* Copy data to new space */
  if (get_num_elements() > 0) {
    memcpy(indices_, temp_indices, get_num_elements());
    memcpy(orig_indices_, temp_orig_indices, get_num_elements());
    memcpy(elements_, temp_elements, get_num_elements());
  }
  /* Free old data */
  delete [] temp_elements;
  delete [] temp_orig_indices;
  delete [] temp_indices;
}
