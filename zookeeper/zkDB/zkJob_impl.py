import os
import zookeeper
from zkEntity_impl import zkEntity
from zkProject_impl import zkProject
from zkInput_impl import zkInput

class zkJob(zkEntity):

  __tmpProject = None
  __tmpInput = None
  __tmpFrames = None

  def __init__(self, connection, id = None):
    super(zkJob, self).__init__(connection, table = 'job', id = id)
    self.__tmpProject = None
    self.__tmpInput = None
    self.__tmpFrames = []

  def __getProject(self):
    if self.id is None:
      return self.__tmpProject
    return zkProject(self.connection, self.projectid)

  def __setProject(self, value):
    self.__tmpProject = value

  def __getInput(self):
    if self.id is None:
      return self.__tmpInput
    return zkInput(self.connection, self.inputid)

  def __setInput(self, value):
    self.__tmpInput = value

  project = property(__getProject, __setProject)
  input = property(__getInput, __setInput)

  def pushFrameForSubmit(self, frame):
    self.__tmpFrames += [frame]

  @property
  def framesForSubmit(self):
    return self.__tmpFrames

  def write(self):

    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
    if not self.__tmpInput is None:
      self.inputid = self.__tmpInput.id
      self.__tmpInput = None

    super(zkJob, self).write()

    if len(self.__tmpFrames) > 0:

      frames = []
      for i in range(len(self.__tmpFrames)):
        f = self.__tmpFrames[i]
        frames += [[
          str(self.projectid),
          str(self.id),
          str(f.priority if f.priority else 50),
          str(f.package if f.package else 1),
          str(f.time if f.time else 0),
          str(f.timeend if f.timeend else 0)
        ]]

      sql = "INSERT into frame (frame_projectid, frame_jobid, frame_priority, frame_package, frame_time, frame_timeend) VALUES "

      for i in range(len(frames)):
        if i > 0:
          sql += ','
        sql += '(' + ','.join(frames[i]) + ')'
      sql += ';'
      self.connection.execute(sql)

      self.__tmpFrames = []      

  def getAllFrames(self):
    return zookeeper.zkDB.zkFrame.getAll(self.connection, condition = 'frame_jobid=%d' % self.id)

  def getWaitingFrames(self):
    return zookeeper.zkDB.zkFrame.getAll(self.connection, condition = 'frame_jobid=%d AND frame_status=\"%s\";' % (self.id,'WAITING'))

  def getCompletedFrames(self):
    return zookeeper.zkDB.zkFrame.getAll(self.connection, condition = 'frame_jobid=%d AND frame_status=\"%s\";' % (self.id, 'COMPLETED'))

  def getDeliveredFrames(self):
    return zookeeper.zkDB.zkFrame.getAll(self.connection, condition = 'frame_jobid=%d AND frame_status=\"%s\";' % (self.id, 'DELIVERED'))

  def getFailedFrames(self):
    return zookeeper.zkDB.zkFrame.getAll(self.connection, condition = 'frame_jobid=%d AND frame_status=\"%s\";' % (self.id, 'FAILED'))

  def getScratchKey(self):
    return '%s_%d' % (self.name, self.id)

  def getScratchFolder(self, config):
    projectFolder =self.project.getScratchFolder(config)
    if projectFolder is None:
      return None
    return os.path.join(projectFolder, 'jobs', self.getScratchKey())
