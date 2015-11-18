import os
import shutil
import fnmatch
from win_unc.internal.current_state import get_current_net_use_table

def zk_resolveEnvVarsInPath(path):
  if path.startswith('$'):
    parts = path.replace('\\', '/').partition('/')
    if os.environ.has_key(parts[0][1:]):
      path = os.path.normpath(os.environ[parts[0][1:]] + parts[1] + parts[2])
  return path

def zk_uncFromDrivePath(path):
  print 'zk_uncFromDrivePath'
  print path
  drive = os.path.splitdrive(path)[0]
  print drive
  if drive:
    if drive[1] == ':':
      table = get_current_net_use_table()
      for row in table.rows:
        if drive.lower() == row['local'].get_drive().lower():
          unc = row['remote'].get_path()
          print unc
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

def zk_findFilesGenerator(directory, pattern = None):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if pattern:
              if not fnmatch.fnmatch(basename, pattern):
                continue
            filename = os.path.join(root, basename)
            yield filename

def zk_findFiles(directory, pattern = None):
  result = []
  for f in zk_findFilesGenerator(directory, pattern):
    result += [f]
  return result

def zk_synchronizeFile(source, target, folderCache = None):
  if not os.path.exists(source):
    return (None, None)

  targetFolder = os.path.split(target)[0]

  # ensure to only check if a folder exists if we didn't see it yet
  targetFolderExists = False
  if folderCache:
    if folderCache.has_key(targetFolder):
      targetFolderExists = True
    else:
      targetFolderExists = os.path.exists(targetFolder)
      folderCache[targetFolder] = True
  else:
    targetFolderExists = os.path.exists(targetFolder)
  if not targetFolderExists:
    os.makedirs(targetFolder)

  reasonForCopy = None
  if os.path.exists(target):
    sourceStat = os.stat(source)
    targetSTat = os.stat(target)
    if not str(sourceStat.st_size) == str(targetSTat.st_size):
      needsToCopy = True
      reasonForCopy = 'file sizes differ.'
    elif not str(sourceStat.st_mtime) == str(targetSTat.st_mtime):
      needsToCopy = True
      reasonForCopy = 'file modified times differ.'
  else:
    needsToCopy = True
    reasonForCopy = 'file did not exist.'
  if reasonForCopy:
    shutil.copyfile(source, target)
    shutil.copystat(source, target)
  return (target, reasonForCopy)

def zk_synchronizeFolder(source, target, pattern = None, logFunc = None):
  if target.startswith(source):
    raise Exception("target is a subset of source.")

  folderCache = {}

  files = zk_findFiles(source, pattern)
  result = []
  for f in files:
    relPath = os.path.relpath(f, source)
    absPath = os.path.join(target, relPath)
    (resultPath, reason) = zk_synchronizeFile(f, absPath, folderCache)
    if reason:
      message = "Synchronized %s because %s." % (f, reason)
      if logFunc:
        logFunc(message)
      else:
        print message
    result += [resultPath]
  return result

def zk_createSynchronizeTargetPath(sourceFolder, targetFolder, path):
  try:
    relPath = os.path.relpath(path, sourceFolder)
    return os.path.join(targetFolder, relPath)
  except:
    pass
  p = path.replace('\\', '/')
  if p[1] == ':': # windows drive
    p = 'drives/%s%s' % (p[0], p[2:])
  elif p.startswith('//'): # unc path
    p = 'unc/'+p[2:]
  return os.path.normpath(os.path.join(targetFolder, p))
 
def zk_synchronizeFilesBetweenFolders(files, sourceFolder, targetFolder, logFunc = None):
  result = []
  for f in files:
    f2 = zk_createSynchronizeTargetPath(sourceFolder, targetFolder, f)
    (f3, reason) = zk_synchronizeFile(f, f2)
    if reason:
      message = "Synchronized %s because %s." % (f, reason)
      if logFunc:
        logFunc(message)
      else:
        print message
    result += [f3]
  return result

