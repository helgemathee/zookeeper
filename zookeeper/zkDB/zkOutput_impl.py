import os
from zkEntity_impl import zkEntity
from zkProject_impl import zkProject
from zkJob_impl import zkJob
from zkFrame_impl import zkFrame

class zkOutput(zkEntity):

  __tmpProject = None
  __tmpJob = None
  __tmpFrame = None

  def __init__(self, connection, id = None):
    super(zkOutput, self).__init__(connection, table = 'output', id = id)
    self.__tmpProject = None
    self.__tmpJob = None
    self.__tmpFrame = None

  def __getProject(self):
    if self.id is None:
      return self.__tmpProject
    return zkProject(self.connection, self.projectid)

  def __setProject(self, value):
    self.__tmpProject = value

  def __getJob(self):
    if self.id is None:
      return self.__tmpJob
    return zkJob(self.connection, self.jobid)

  def __setJob(self, value):
    self.project = value.project
    self.__tmpJob = value

  def __getFrame(self):
    if self.id is None:
      return self.__tmpFrame
    return zkFrame(self.connection, self.frameid)

  def __setFrame(self, value):
    self.job = value.job
    self.__tmpFrame = value

  project = property(__getProject, __setProject)
  job = property(__getJob, __setJob)
  frame = property(__getFrame, __setFrame)

  @property
  def ext(self):
    return os.path.splitext(self.path)[1][1:]

  def write(self):
    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
    if not self.__tmpJob is None:
      self.jobid = self.__tmpJob.id
      self.__tmpJob = None
    if not self.__tmpFrame is None:
      self.frameid = self.__tmpFrame.id
      self.__tmpFrame = None

    super(zkOutput, self).write()

  def getScratchKey(self):
    time = str(self.frame.time).rjust(5, '0')
    return self.name+'_'+time+'_'+str(self.id)+'.'+self.ext

  def getScratchFile(self, config):
    folder = self.frame.getScratchFolder(config)
    enabled = config.get('scratchdisc_enabled', False)
    if not enabled:
      return None
    return os.path.join(folder, self.name, self.getScratchKey())  
