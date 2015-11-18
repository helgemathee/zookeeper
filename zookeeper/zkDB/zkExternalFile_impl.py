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
    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s WHERE %s_projectid = %d AND %s_resolvedpath = %s;' % (table, table, table, projectid, table, repr(str(resolvedPath)))
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    extFile = cls(conn)
    extFile.projectid = projectid
    extFile.userpath = userPath
    extFile.resolvedpath = resolvedPath
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
    networkPath = self.resolvedpath

    # correct unc paths
    if uncMap:
      for u in uncMap:
        if networkPath.lower().startswith(u.lower()):
          networkPath = uncMap[u] + networkPath[len(u):]
          break

    networkFile = os.path.split(networkPath)[1]
    networkParts = networkFile.rpartition('.')

    scratchDisc = self.project.getScratchFolder(cfg)
    scratchFolder = os.path.join(scratchDisc, self.type)
    scratchPath = os.path.join(scratchFolder, networkParts[0]+'_id'+str(self.id)+'.'+networkParts[2])

    (resultPath, reasonForCopy) = zookeeper.zkClient.zk_synchronizeFile(networkPath, scratchPath)
    if reasonForCopy:
      message = 'ZooKeeper: updated cache for '+networkPath+' because '+reasonForCopy
      if logFunc:
        logFunc(message)
      else:
        print message

    return resultPath
