#!/usr/bin/env python

import os

def get_num_cpus():
  """Returns the number of CPUs on a system."""
  # Linux, Unix and MacOS
  if hasattr(os, "sysconf"):
    if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
      # Linux and Unix
      ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
      if isinstance(ncpus, int) and ncpus > 0:
        return ncpus
    else: # OSX
      return int(os.popen2("sysctl -n hw.ncpu")[1].read())
  # Windows
  if os.environ.has_key("NUMBER_OF_PROCESSORS"):
    ncpus = int(os.environ["NUMBER_OF_PROCESSORS"]);
    if ncpus > 0:
      return ncpus
  return 1
