/*
 * Copyright (c) 2012 Alexander Sviridenko
 */

/**
 * @file packed_vector.hpp
 * @brief Packed vector.
 */

#ifndef __LES_PACKED_VECTOR_HPP
#define __LES_PACKED_VECTOR_HPP

#include <map>

using namespace std;

/*
 * Use i-th index or element by position use get_indices()[i] or
 * get_elements()[i]. 
 */

class PackedVector
{
public:
  /** Default constructor */
  PackedVector();

  void init(size_t size, const int* indices, double* elements);
  void init(vector<int>& indices);
  void init(vector<int>& indices, vector<double>& elements);

  inline int size() const { return get_num_elements(); }
  inline int get_num_elements() const { return nr_elements_; }

  /**
   * Reset the vector, as it was just created an empty vector.
   */
  void clear();

  /** Return pointer to the array of elements. */
  const double* get_elements() const { return elements_; }

  double get_element(int pos) { return get_element_by_pos(pos); }

  /**
   * Get element value by its position.
   */
  double get_element_by_pos(int pos) { return elements_[pos]; }

  bool has_element(int index)
  {
    map<int, int>::iterator it;
    it = index_to_pos_mapping_.find(index);
    return (it != index_to_pos_mapping_.end());
  }

  /**
   * Get element by index. If element doesn't exist return WHAT?. On
   * this moment we return 0.0.
   */
  double get_element_by_index(int i)
  {
    map<int, int>::iterator it;
    it = index_to_pos_mapping_.find(i);
    if (it == index_to_pos_mapping_.end())
      return 0.0;
    return get_element_by_pos(it->second);
  }

  int* get_indices() const { return indices_; }

  /**
   * Set an existing element in the packed vector.
   * The first argument is the "index" into the elements() array.
   * See set_element_by_pos() and get_element_by_pos().
   */
  void set_element(int index, double element)
  {
    set_element_by_pos(index, element);
  }

  void set_element_by_pos(int index, double element)
  {
    elements_[index] = element;
  }

  void zero();

  inline int get_index(int pos) { return get_index_by_pos(pos); }

  /**
   * Get vector of indices of elements.
   */
  inline int get_index_by_pos(int pos) { return indices_[pos]; }

  /**
   * Insert an element into the vector.
   */
  void insert(int index, double element);

private:
  void reserve(int n);
  map<int, int> index_to_pos_mapping_;
  int* indices_; /* Pointer to vector of indices. */
  int* orig_indices_; /* original unsorted indices */
  double* elements_; /* Pointer to vector of elements_. */
  int nr_elements_; /* Size of indices_ and elements_ vectors. */
  int capacity_; /* Amount of memory allocated for indices_,
                    orig_indices_, and elements_. */
};

#endif /* __LES_PACKED_VECTOR_HPP */
