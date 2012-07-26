// Copyright (c) 2012 Alexander Sviridenko

#include <les/packed_matrix.hpp>

// Convert CoinPackedVector for coin-or library to PackedVector.
static void
convert_CoinPackedVector_to_PackedVector(CoinShallowPackedVector* src,
                                         PackedVector* dst)
{
  dst->init(src->getNumElements(), src->getIndices(), src->getElements());
  //for (int i = 0; i < src->getNumElements(); i++)
  //  dst->insert(src->getIndices()[i], src->getElements()[i]);
}

/* FIXME: some sheet happens here. */
PackedVector*
PackedMatrix::get_vector(int i) const
{
  if (i > get_num_rows())
    {
      return NULL;
    }
  CoinShallowPackedVector src = slave_matrix_.getVector(i);
  //if (!src)
  //  return NULL;
  PackedVector* dst = new PackedVector();
  convert_CoinPackedVector_to_PackedVector(&src, dst);
  return dst;
}

vector<int>*
PackedMatrix::get_nonzero_rows() const
{
  vector<int>* nonzero_rows = new vector<int>();
  for (int i = 0; i < get_num_rows(); i++)
    {
      if (slave_matrix_.getVectorLengths()[i] > 0)
        nonzero_rows->push_back(i);
    }
  return nonzero_rows;
}

vector<int>*
PackedMatrix::get_nonzero_cols() const
{
  map<int, bool> cols_map;
  for (int i = 0; i < get_num_rows(); i++)
    {
      const int* indices = slave_matrix_.getIndices() +
        slave_matrix_.getVectorStarts()[i];
      for (int j = 0; j < slave_matrix_.getVectorLengths()[i]; j++)
        {
          cols_map[ indices[j] ] = true;
        }
    }
  /* Copy keys (cols) to special vector */
  vector<int>* nonzero_cols = new vector<int>();
  for(map<int, bool>::iterator it = cols_map.begin();
      it != cols_map.end(); ++it )
    {
      nonzero_cols->push_back( it->first );
    }
  return nonzero_cols;
}
