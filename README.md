<!--- -*- mode: markdown; -*- --->

Local Elimination Solver (LES)

Copyright (c) 2012-2013 Oleksandr Sviridenko

What is LES?
------------

LES is a framework for solving a class of mathematical problems called
[binary integer linear programming](http://en.wikipedia.org/wiki/Integer_linear_programming)
(BILP) problems and its variants with help of local elimination algorithms
(LEA).

What is it for, anyway?
-----------------------

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

License
-------

This software is licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html). See the included NOTICE
file for more information.

Maintainers
-----------

Oleksandr Sviridenko, Oleg Shcherbina, Dariana Lemtuzhnikova,
[Irina Shapovalova](https://github.com/IreneZR/les).
