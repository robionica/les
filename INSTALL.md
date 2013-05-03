Third party dependencies
------------------------

Some of the solvers and decomposers depend on third party software, that have to
be installed manually. Please install required dependencies before you will
start installing LES, if you're going to use them.

Solvers:

* `OsiSymSolverInterface` and `OsiClpSolverInterface` require [SYMPHONY](https://projects.coin-or.org/SYMPHONY)
* `GLPSolver` requires [GLPK](http://www.gnu.org/software/glpk/)
* `SCIPSolver` requires [SCIP](http://scip.zib.de/)

Decomposers:

* `MetisPartGraphDecomposer` requires [METIS](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview).

Installation -- Linux
---------------------

1. Download the latest version of LES:

        $ git clone git@github.com:d2rk/les.git

2. To install LES, make sure you have Python 2.7 or greater installed. If you're
   in doubt, run:

        $ python -V

3. Install extra software and setup environment. Please install at least one
   master solver,
   e.g. [SYMPHONY](https://github.com/d2rk/les/blob/master/docs/install_symphony.md#install-symphony),
   in order to use Local Elimination Solver.

4. Run this command from the command prompt:

        $ python setup.py develop

5. Run the tests:

        $ python setup.py test

   If some tests fail, this library may not work correctly on your
   system. Continue at your own risk.

NOTE: on this moment we're using "development mode" to skip direct installation
process. Once the work has been done you can remove the project source from a
staging area using `$ python setup.py develop --uninstall`.