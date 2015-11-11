import copy
from zkDialog_impl import zkDialog
from zookeeper.zkConfig_impl import zkConfig

class zkConfigDialog(zkDialog):

  __config = None

  def __init__(self, parent = None):
    self.__config = zkConfig()

    super(zkConfigDialog, self).__init__(parent)

  def getDialogName(self):
    return 'Configuration'
  
  def getFields(self):
    return copy.deepcopy(self.__config.getFields())

  def onAccepted(self, fields):
    for field in fields:
      self.__config.set(field['name'], field['value'], field['type'])
