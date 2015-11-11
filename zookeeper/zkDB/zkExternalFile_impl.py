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

