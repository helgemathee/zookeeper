from zkEntity_impl import zkEntity
from zkMachine_impl import zkMachine
from zkFrame_impl import zkFrame

class zkNotification(zkEntity):

  __tempMachine = None
  __tempFrame = None

  def __init__(self, connection, id = None):
    super(zkNotification, self).__init__(connection, table = 'notification', id = id)
    self.__tempMachine = None
    self.__tempFrame = None

  def __getMachine(self):
    if self.id is None:
      return self.__tempMachine
    return zkMachine(self.connection, self.machineid)

  def __setMachine(self, value):
    self.__tempMachine = value

  def __getFrame(self):
    if self.id is None:
      return self.__tempFrame
    return zkFrame(self.connection, self.frameid)

  def __setFrame(self, value):
    self.__tempFrame = value

  machine = property(__getMachine, __setMachine)
  frame = property(__getFrame, __setFrame)

  def write(self):

    if not self.__tempMachine is None:
      self.machineid = self.__tempMachine.id
      self.__tempMachine = None
    if not self.__tempFrame is None:
      self.frameid = self.__tempFrame.id
      self.__tempFrame = None

    super(zkNotification, self).write()

