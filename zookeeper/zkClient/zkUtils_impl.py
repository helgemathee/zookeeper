import os
from win_unc.internal.current_state import get_current_net_use_table

def zk_resolveEnvVarsInPath(path):
  if path.startswith('$'):
    parts = path.replace('\\', '/').partition('/')
    if os.environ.has_key(parts[0][1:]):
      path = os.path.normpath(os.environ[parts[0][1:]] + parts[1] + parts[2])
  return path

def zk_uncFromDrivePath(path):
  drive = os.path.splitdrive(path)[0]
  if drive:
    if drive[1] == ':':
      table = get_current_net_use_table()
      for row in table.rows:
        if drive.lower() == row['local'].get_drive().lower():
          unc = row['remote'].get_path()
          uncpath = os.path.normpath(unc + '\\' + path[2:])
          return uncpath
  return path

def zk_validateFilePath(path, shouldExist=True):
  path = zk_resolveEnvVarsInPath(path)
  if shouldExist:
    try:
      os.stat(path)
    except:
      return False
  return True

def zk_validateNetworkFilePath(path, validUncPaths = None, shouldExist=True):
  if not zk_validateFilePath(path, shouldExist):
    return False

  path = zk_resolveEnvVarsInPath(path)
  drive = os.path.splitdrive(path)[0]
  if drive[1] == ":":
    uncpath = zk_uncFromDrivePath(path)
    if uncpath == path and uncpath[1] == ':':
      # local drive
      return False

    if validUncPaths:
      found = False
      for validUncPath in validUncPaths:
        if uncpath.lower().startswith(validUncPath.lower()):
          found = True
          break
      if not found:
        return False

    path = uncpath

    if shouldExist:
      try:
        os.stat(path)
      except:
        return False

  return True
