from zkEntity_impl import zkEntity
from zkProject_impl import zkProject
from zkJob_impl import zkJob

class zkFrame(zkEntity):

  __tmpProject = None
  __tmpJob = None

  def __init__(self, connection, id = None):
    super(zkFrame, self).__init__(connection, table = 'frame', id = id)
    self.__tmpProject = None
    self.__tmpJob = None

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

  project = property(__getProject, __setProject)
  job = property(__getJob, __setJob)

  def write(self):

    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
    if not self.__tmpJob is None:
      self.jobid = self.__tmpJob.id
      self.__tmpJob = None

    super(zkFrame, self).write()

