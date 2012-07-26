// Copyright (c) 2012 Alexander Sviridenko

/**
 * @file packed_vector.hpp
 * @brief Packed vector.
 */

#ifndef __LES_PACKED_VECTOR_HPP
#define __LES_PACKED_VECTOR_HPP

#include <map>
#include <iostream>
#include <assert.h>

using namespace std;

/*
 * Use i-th index or element by position use get_indices()[i] or
 * get_elements()[i].
 */

class PackedVector
{
public:
  // Default constructor.
  PackedVector();

  // Initialization
  void init(size_t size, const int* indices, const double* elements);
  void init(vector<int>& indices);
  void init(vector<int>& indices, vector<double>& elements);

  inline int size() const
  {
    return get_num_elements();
  }

  inline int get_num_elements() const
  {
    return nr_elements_;
  }

  // Resizes the vector to contain n elements.
  void resize(size_t n);

  // Reset the vector, as it was just created an empty vector.
  void clear();

  // Return pointer to the array of elements.
  inline const double* get_elements() const
  {
    return elements_;
  }

  // Just an alias for get_element_by_pos().
  inline double get_element(int pos)
  {
    return get_element_by_pos(pos);
  }

  // Get element value by its position.
  double get_element_by_pos(int pos)
  {
    return elements_[pos];
  }

  bool has_element(int index)
  {
    map<int, int>::iterator it;
    it = index_to_pos_mapping_.find(index);
    return (it != index_to_pos_mapping_.end());
  }

  // Get element by index.
  // XXX: if element doesn't exist return WHAT?. On this moment we return 0.0.
  double get_element_by_index(int i);

  int* get_indices() const
  {
    return indices_;
  }

  void set_element(int pos, double element)
  {
    set_element_by_pos(pos, element);
  }

  // Set an existing element in the packed vector.
  // The first argument is the "pos" into the elements() array.
  // See set_element_by_pos() and get_element_by_pos().
  void set_element_by_pos(int pos, double element)
  {
    elements_[pos] = element;
  }

  void set_element_by_index(int i, double element)
  {
    insert(i, element);
  }

  void zero();

  inline int get_index(int pos)
  {
    return get_index_by_pos(pos);
  }

  // Get vector of indices of elements.
  inline int get_index_by_pos(int pos)
  {
    assert(pos < get_num_elements());
    return indices_[pos];
  }

  // Insert an element into the vector.
  void insert(int i, double element);

  void dump()
  {
    for (int i = 0; i < get_num_elements(); i++)
      cout << "\t" << get_index(i) << "\t\t" << get_element(i) << endl;
  }

private:
  void reserve(int n);
  map<int, int> index_to_pos_mapping_;
  int* indices_; /* Pointer to vector of indices. */
  int* orig_indices_; /* original unsorted indices */
  double* elements_; // Pointer to vector of elements_.
  int nr_elements_; // Size of indices_ and elements_ vectors.
  int capacity_; // Amount of memory allocated for indices_,
                 // orig_indices_, and elements_.
};

#endif /* __LES_PACKED_VECTOR_HPP */
