/*
 * Copyright (c) 2011 Alexander Sviridenko
 */
 
#ifndef __LES_UTILS_HXX
#define __LES_UTILS_HXX

#include <stddef.h>
#include <vector>

void convert_dec_to_bin(int dec, std::vector<int>* bin, unsigned n=0);
int convert_bin_to_dec(double* bin, size_t sz);

#endif /* __LES_UTILS_HXX */

