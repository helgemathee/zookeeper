import os
import shutil
import zookeeper
from zkEntity_impl import zkEntity
from zkProject_impl import zkProject

class zkExternalFile(zkEntity):

  __tmpProject = None

  def __init__(self, connection, id = None):
    super(zkExternalFile, self).__init__(connection, table = 'externalfile', id = id)
    self.__tmpProject = None

  def __getProject(self):
    if self.id is None:
      return self.__tmpProject
    return zkProject(self.connection, self.projectid)

  def __setProject(self, value):
    self.__tmpProject = value

  project = property(__getProject, __setProject)

  def write(self):

    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
      
    super(zkExternalFile, self).write()

  @classmethod
  def getOrCreateByProjectAndPaths(cls, conn, projectid, userPath, resolvedPath, type = 'otherfile', resolution = -1):
    realUserPath = userPath
    realResolvedPath = resolvedPath
    if userPath.find('..') > -1:
      parts = realResolvedPath.rpartition('[')
      realResolvedPath = parts[0] + '#' + parts[2].partition(']')[2]
      parts = realUserPath.rpartition('[')
      realUserPath = parts[0] + '#' + parts[2].partition(']')[2]

    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s WHERE %s_projectid = %d AND %s_resolvedpath = %s;' % (table, table, table, projectid, table, repr(str(realResolvedPath)))
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    extFile = cls(conn)
    extFile.projectid = projectid

    if userPath.find('..') > -1:
      parts = userPath.rpartition('[')
      frameSection = parts[2].partition(']')[0]
      extFile.start = frameSection.partition('..')[0]
      extFile.end = frameSection.partition('..')[2].partition(';')[0]
      extFile.padding = frameSection.partition('..')[2].partition(';')[2]
      if extFile.padding == '':
        extFile.padding = 0

    extFile.userpath = realUserPath
    extFile.resolvedpath = realResolvedPath
    extFile.type = type
    extFile.resolution = resolution
    extFile.write()
    return extFile

  @classmethod
  def getByProjectAndUserPath(cls, conn, projectid, userPath):
    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s WHERE %s_projectid = %d AND %s_userpath = %s;' % (table, table, table, projectid, table, repr(str(userPath)))
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    return None

  def getScratchDiskPath(self, cfg):
    networkPath = self.resolvedpath
    networkFile = os.path.split(networkPath)[1]
    networkParts = networkFile.rpartition('.')
    scratchDisc = self.project.getScratchFolder(cfg)
    scratchFolder = os.path.join(scratchDisc, self.type)
    scratchPath = os.path.join(scratchFolder, networkParts[0]+'_id'+str(self.id)+'.'+networkParts[2])
    return scratchPath

  def synchronize(self, cfg, uncMap = None, logFunc = None):
    numFrames = 1
    print str(self.id) + ': ' + str(self.start) + ' - ' + str(self.end)
    if not self.end is None and not self.start is None:
      numFrames = self.end - self.start + 1
    result = None
    for i in range(numFrames):
      f = str(int(self.start) + i)
      f = f.rjust(int(self.padding), '0')
      networkPath = self.resolvedpath

      # correct unc paths
      if uncMap:
        for u in uncMap:
          if networkPath.lower().startswith(u.lower()):
            networkPath = uncMap[u] + networkPath[len(u):]
            break

      realNetworkPath = networkPath.replace('#', f)

      networkFile = os.path.split(realNetworkPath)[1]
      networkParts = networkFile.rpartition('.')

      scratchDisc = self.project.getScratchFolder(cfg)
      scratchFolder = os.path.join(scratchDisc, self.type)
      scratchPath = os.path.join(scratchFolder, networkParts[0]+'_id'+str(self.id)+'.'+networkParts[2])

      (resultPath, reasonForCopy) = zookeeper.zkClient.zk_synchronizeFile(realNetworkPath, scratchPath)
      if reasonForCopy:
        message = 'ZooKeeper: updated cache for '+realNetworkPath+' because '+reasonForCopy
        if logFunc:
          logFunc(message)
        else:
          print message
      if not result and resultPath:
        result = os.path.join(os.path.split(resultPath)[0], os.path.split(scratchPath)[1])

    return result
