# Install SYMPHONY

## Install on Linux

### Install from binaries

Download the binaries from <http://www.coin-or.org/download/binary/SYMPHONY/>,
for example [SYMPHONY-5.2.0-Linux-x86-Install](http://www.coin-or.org/download/binary/SYMPHONY/SYMPHONY-5.2.0-Linux-x86-Install), move
to the directory with installer and run installation process:

    $ wget http://www.coin-or.org/download/binary/SYMPHONY/SYMPHONY-5.2.0-Linux-x86-Install
    $ chmod +x SYMPHONY-5.2.0-Linux-x86-Install
    $ ./SYMPHONY-5.2.0-Linux-x86-Install

Installer will ask you to select library home directory, for example
`/home/d2rk/SYMPHONY/`.

## Setup

Once SYMPHONY was installed, you need to edit config.mk. Open it and
find the following line:

    COINOR_HOME_DIR_PATH =

Edit it according to SYMPHONY home directory, for instance:

    COINOR_HOME_DIR_PATH = /home/d2rk/SYMPHONY

## Known issues

*      CoinFinite.hpp: In function ‘bool CoinIsnan(double)’:
           CoinFinite.hpp: 109 :26: error: ‘_isnan’ was not declared in this scope

  Open file `config_coinutils.h` (in my case it can find found
  in `/home/d2rk/SYMPHONY/include/coin`) and find the following lines:

           /* Define to be the name of C-function for NaN check */
           #define MY_C_ISNAN _isnan

  Change `MY_C_ISNAN` value to `isnan`.
