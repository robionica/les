/*
 * Copyright (c) 2012 Alexander Sviridenko
 */
#include <math.h>

#include <les/utils/math.hpp>

/**
 * Convert decimal number to binary. The binary representation is stored as
 * vector with specified number of digits.
 *
 * @param dec  Decimal value
 * @param bin  Reference to vector where binary will be stored.
 * @param n    Required number of digits
 */
void
convert_dec_to_bin(int dec, std::vector<int>* bin, unsigned n)
{
  while (dec > 0)
    {
      if ((dec & 1) == 1)
        bin->insert(bin->begin(), 1);
      else
        bin->insert(bin->begin(), 0);
      dec >>= 1;
    }
  /* Add lead zeros if required */
  if (n && bin->size() < n)
    bin->insert(bin->begin(), n - bin->size(), 0);
}

/**
 * Return decimal representation.
 *
 * @param bin Binary representation
 */
int
convert_bin_to_dec(double* bin, size_t sz)
{
  int dec = 0;
  int tmp;

  for (int i = sz - 1; i >= 0; i--)
    {
      tmp = (int)pow(2, sz - (i + 1));
      dec += tmp * (int)bin[i];
    }

  return dec;
}
