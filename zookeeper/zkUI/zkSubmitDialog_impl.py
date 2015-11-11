import copy
from zkCallbackDialog_impl import zkCallbackDialog

class zkSubmitDialog(zkCallbackDialog):

  __fields = None

  def __init__(self, fields, onAcceptedCallback, parent = None):
    self.__fields = fields
    super(zkSubmitDialog, self).__init__(onAcceptedCallback, None, parent)

  def getDialogName(self):
    return 'Submit Job'
  
  def getFields(self):
    return copy.deepcopy(self.__fields)

