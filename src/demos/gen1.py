#!/usr/bin/env python
#
# Copyright (c) 2013 Oleksandr Sviridenko
#
# This demo shows how to generate random quasi-block BILP model that has N
# variables and M constraints.

from les.mp_model_generators import qbbilp_model_generator

N = 9
M = 6

def main():
  generator = qbbilp_model_generator.QBBILPModelGenerator()
  model = generator.gen(num_constraints=M, num_variables=N)
  model.pprint()

if __name__ == '__main__':
  main()
