
# SYMPHONY solver support

## Install SYMPHONY

### Installing from binaries

Download the binaries from <http://www.coin-or.org/download/binary/SYMPHONY/>,
for example [SYMPHONY-5.2.0-Linux-x86-Install](http://www.coin-or.org/download/binary/SYMPHONY/SYMPHONY-5.2.0-Linux-x86-Install). Move
to the directory with installer and run installation process:

    chmod +x SYMPHONY-5.2.0-Linux-x86-Install
    ./SYMPHONY-5.2.0-Linux-x86-Install

Installer will ask you to select library home directory, for example
`/home/d2rk/SYMPHONY/`.

### Installing on Ubuntu

This section requires update.

     sudo apt-get install coinor-libsymphony-dev coinor-libcoinutils-dev \
     coinor-libosi-dev coinor-libcgl-dev coinor-libclp-dev

Read more about deb packages https://projects.coin-or.org/CoinBinary/wiki/CoinDeb.

## Setup solver

Once SYMPHONY was installed, you need to edit Makefile. Open it and
find the following line:

    COINOR_SYMPHONY_DIR =

and edit it according to SYMPHONY home directory, for instance:

    COINOR_SYMPHONY_DIR = /home/d2rk/SYMPHONY

Next, build it:

    make

## Known issues

*      CoinFinite.hpp: In function ‘bool CoinIsnan(double)’:
       CoinFinite.hpp:109:26: error: ‘_isnan’ was not declared in this scope

  Open file `config_coinutils.h` (in my case it can find found
  in `/home/d2rk/SYMPHONY/include`) and find the following lines:

       /* Define to be the name of C-function for NaN check */
       #define MY_C_ISNAN _isnan

  Change `MY_C_ISNAN` to `isnan`.