import os

def zk_uncFromDrivePath(path):
  drive = os.path.splitdrive(path)[0]
  if drive[1] == ':':
    from win_unc.internal.current_state import get_current_net_use_table
    table = get_current_net_use_table()
    for row in table.rows:
      if drive.lower() == row['local'].get_drive().lower():
        unc = row['remote'].get_path()
        uncpath = os.path.normpath(unc + '\\' + path[2:])
        return uncpath
  return path

def zk_validateFilePath(path):
  try:
    os.stat(path)
  except:
    return False
  return True

def zk_validateNetworkFilePath(path):
  if not zk_validateFilePath(path):
    return False

  drive = os.path.splitdrive(path)[0]
  if drive[1] == ":":
    uncpath = zk_uncFromDrivePath(path)
    if uncpath == path:
      # local drive
      return False
    path = uncpath

    try:
      os.stat(path)
    except:
      return False

  return True
