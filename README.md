
# Local Elimination Solver (LES)

Copyright (c) 2012 Alexander Sviridenko

## What is LES?

LES is a library for solving a class of mathematical problems called
[integer linear
programming](http://en.wikipedia.org/wiki/Integer_linear_programming)
(ILP) problems and its variants with help of local elimination
algorithms.

## Installing on Ubuntu

First, of all, you need to install prerequisites:

       sudo apt-get install gcc g++ git make

LES is also required some [Boost](http://www.boost.org/) libraries.
They can be installed [manually](http://www.boost.org/doc/libs/1_48_0/more/getting_started/unix-variants.html#easy-build-and-install)
or from repository:

      sudo apt-get install libboost-all-dev

Next, get the sources and build it:

      git clone git://github.com/d2rk/les.git
      cd les
      make

## Getting Started

Add path to LES library for your projects:

    LD_LIBRARY_PATH=/somewhere/les/lib/

