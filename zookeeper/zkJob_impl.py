from zkEntity_impl import zkEntity
from zkProject_impl import zkProject
from zkInput_impl import zkInput

class zkJob(zkEntity):

  __tmpProject = None
  __tmpInput = None

  def __init__(self, connection, id = None):
    super(zkJob, self).__init__(connection, table = 'job', id = id)
    self.__tmpProject = None
    self.__tmpInput = None

  def __getProject(self):
    if self.jobid is None:
      return self.__tmpProject
    return zkProject(self.connection, self.projectid)

  def __setProject(self, value):
    self.__tmpProject = value

  project = property(__getProject, __setProject)

  def __getInput(self):
    if self.jobid is None:
      return self.__tmpInput
    return zkInput(self.connection, self.inputid)

  def __setInput(self, value):
    self.__tmpInput = value

  input = property(__getInput, __setInput)

  def write(self):

    if not self.__tmpProject is None:
      self.projectid = self.__tmpProject.id
      self.__tmpProject = None
    if not self.__tmpInput is None:
      self.inputid = self.__tmpInput.id
      self.__tmpInput = None

    super(zkJob, self).write()

