# Install SCIP

LES is using [python-zibopt](https://pypi.python.org/pypi/python-zibopt/) as
python interface.

How to build and install SCIP from source:

1. Download the latest source code of ZIBopt (e.g. v2.1.1), unarachive it and
   compile:

        $ tar xvfz ziboptsuite-2.1.1.tgz
        $ cd ziboptsuite-2.1.1/
        $ make ziboptlib SHARED=true ZIMPL=false READLINE=false

2. Copy scipopt library to your library directory (e.g. `$HOME/.local/lib`) and
   create a symbolic link to their latest version:

        $ cp lib/libzibopt-2.1.1.linux.x86_64.gnu.opt.so ~/.local/lib
        $ ln -s ~/.local/libzibopt-2.1.1.linux.x86_64.gnu.opt.so ~/.local/lib/libscipopt.so

3. In order to build and use `python-zibopt`, we need to reference the C header
   files and `.so` files for ZIBopt in our environment. Once it is built, you'll
   need to keep the `LD_LIBRARY_PATH` set, possibly in your `.bashrc`, in order
   to use it:

        $ export LD_LIBRARY_PATH=$HOME/.local/lib
        $ export C_INCLUDE_PATH=$HOME/downloads/ziboptsuite-2.1.1/scip-2.1.1/src/