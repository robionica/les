/*
 * This file implements celar.hpp interface
 *
 * Copyright (c) 2012 Oleksandr Sviridenko
 */

#include <iostream>
#include <fstream>
#include <string>

#include "celar.hpp"

using namespace std;

void
CELARReader::read(const char* var_txt, const char* dom_txt,
                  const char* ctr_txt, const char* cst_txt)
{
  string line;

  ifstream var_file(var_txt);

  while (getline(var_file, line)) {
    int n, d, v, i;
    var_file >> n >> d >> v >> i;
  }

  ifstream ctr_file(ctr_txt);

  cout << "Parsing " << ctr_txt << endl;
  int cons_id = 0;
  while (getline(ctr_file, line)) {
    int v1, v2;
    char type; /* the constraint type */
    char op; /* operator: "=" or ">" */
    int deviation;
    ctr_file >> v1 >> v2 >> type >> op >> deviation;
    v1--; /* fix values */
    v2--;
    _cons_matrix.set_coefficient(cons_id, v1, 1.0);
    _cons_matrix.set_coefficient(cons_id, v2, 1.0);
    cons_id++;
  }
}
