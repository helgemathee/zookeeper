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
  def getOrCreateByProjectAndPath(cls, conn, projectid, path, type = 'otherfile'):
    table = cls.getTableName()
    sql = 'SELECT %s_id FROM %s WHERE %s_projectid = %d AND %s_path = %s;' % (table, table, table, projectid, table, repr(str(path)))
    ids = conn.execute(sql, errorPrefix=table)
    for id in ids:
      return cls(conn, id=id[0])
    extFile = cls(conn)
    extFile.projectid = projectid
    extFile.path = path
    extFile.type = type
    extFile.write()
    return extFile

  def getScratchDiskPath(self, cfg):
    networkPath = self.path
    networkFile = os.path.split(networkPath)[1]
    networkParts = networkFile.rpartition('.')
    scratchDisc = self.project.getScratchFolder(cfg)
    scratchFolder = os.path.join(scratchDisc, self.type)
    scratchPath = os.path.join(scratchFolder, networkParts[0]+'_id'+str(self.id)+'.'+networkParts[2])
    return scratchPath

  def synchronize(self, cfg, uncMap = None):
    networkPath = self.path

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
      print 'ZooKeeper: updating cache for '+networkPath+' because '+reasonForCopy

    return scratchPath
