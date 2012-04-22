<!--- -*- mode: markdown; -*- --->

# Install SYMPHONY

## Install on Ubuntu

### Install prerequisites

First, of all, you need to install prerequisites:

    $ sudo apt-get install libblas-dev liblapack-dev

### Install SYMPHONY from binaries

Download the binaries from <http://www.coin-or.org/download/binary/SYMPHONY/>,
for example [SYMPHONY-5.2.0-Linux-x86-Install](http://www.coin-or.org/download/binary/SYMPHONY/SYMPHONY-5.2.0-Linux-x86-Install), move
to the directory with installer and run installation process:

    $ wget http://www.coin-or.org/download/binary/SYMPHONY/SYMPHONY-5.2.0-Linux-x86-Install
    $ chmod +x SYMPHONY-5.2.0-Linux-x86-Install
    $ ./SYMPHONY-5.2.0-Linux-x86-Install

Installer will ask you to select library home directory, for example
`/usr/local/`.

## Setup

Once SYMPHONY was installed, you need to let LES know about it:

    $ export SYMPHONY_HOME_DIR=/usr/local/

## Known issues

*      CoinFinite.hpp: In function ‘bool CoinIsnan(double)’:
           CoinFinite.hpp: 109 :26: error: ‘_isnan’ was not declared in this scope

  Open file `config_coinutils.h` (in this case it can be found in
  `/usr/local/include/coin`) and find the following lines:

           /* Define to be the name of C-function for NaN check */
           #define MY_C_ISNAN _isnan

  Change `MY_C_ISNAN` value to `isnan`.

* In case LES doesn't see SYMPHONY libraries (e.g. they were installed to
  `/home/join/local/lib`), do `$ export LD_LIBRARY_PATH=/home/john/local/lib`.
