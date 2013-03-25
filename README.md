<!--- -*- mode: markdown; -*- --->

Local Elimination Solver (LES)

Copyright (c) 2012-2013 Oleksander Sviridenko

## What is LES?

LES is a library for solving a class of mathematical problems called [integer
linear programming](http://en.wikipedia.org/wiki/Integer_linear_programming)
(ILP) problems and its variants with help of local elimination algorithms (LEA).

## What is it for, anyway?

Many real
[discrete optimization](http://en.wikipedia.org/wiki/Discrete_optimization)
problems (DOPs) from [OR](http://en.wikipedia.org/wiki/Operations_research)
applications contain a huge number of variables and/or constraints that make the
models intractable for currently available solvers. Usually, DOPs from
applications have a special structure, and the matrices of constraints for
large-scale problems have a lot of zero elements (sparse matrices), and the
nonzero elements of the matrix often fall into a limited number of blocks. The
block form of many DO problems is usually caused by the weak connectedness of
subsystems of real-world systems.

One of the promising ways to exploit sparsity in the constraint matrix of DO
problems are LEAs, including local decomposition algorithms, nonserial dynamic
programming (NSDP) algorithms.

## Installation

1. Download the latest version of LES:

        $ git clone git@github.com:d2rk/les.git

2. To install LES, make sure you have Python 2.7 or greater installed. If you're
in doubt, run:

        $ python -V

3. Run the tests:

        $ python setup.py test

   If some tests fail, this library may not work correctly on your
   system. Continue at your own risk.

4. Install extra software such as solvers
(e.g. [SYMPHONY](https://github.com/d2rk/les/blob/master/docs/install_symphony.md#install-symphony))
and setup environment.

5. Run this command from the command prompt:

        $ python setup.py develop

NOTE: on this moment we're using "development mode" to skip direct installation
process. Once the work has been done you can remove the project source from a
staging area using `$ python setup.py develop --uninstall`.

## Maintainers

Oleksandr Sviridenko, Oleg Shcherbina, Dariana Lemtuzhnikova.
