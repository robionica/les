import os

for path in (os.path.join(os.environ['OR_TOOLS_HOME_DIR'], 'src', 'gen',
                          'linear_solver'),
             os.path.join(os.environ['OR_TOOLS_HOME_DIR'], 'lib')):
  if not os.path.exists(path):
    raise IOError("Path doesn't exist: %s" % path)
  __path__.append(path)
