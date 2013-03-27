<!--- -*- mode: markdown; -*- --->

Get METIS:

    http://glaros.dtc.umn.edu/gkhome/views/metis

Note that the shared library is needed, and isn't enabled by default
by the configuration process. Turn it on by issuing::

    $ make config shared=1

Your operating system's package manager might know about METIS,
but this wrapper was designed for use with *METIS 5*. Packages with
METIS 4 will not work.

Set `METIS_DLL` variable, e.g.:

    $ export $METIS_DLL=/usr/local/lib/libmetis.so