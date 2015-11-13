import copy
from zkDialog_impl import zkDialog

class zkFieldsDialog(zkDialog):

  __onRejectedCallback = None
  __onAcceptedCallback = None
  __fields = None

  def __init__(self, fields, onAcceptedCallback, onRejectedCallback, parent = None):
    self.__fields = fields
    self.__onAcceptedCallback = onAcceptedCallback
    self.__onRejectedCallback = onRejectedCallback
    super(zkFieldsDialog, self).__init__(parent)

  def onCanceled(self):
    if self.__onRejectedCallback:
      self.__onRejectedCallback()

  def onAccepted(self, fields):
    if self.__onAcceptedCallback:
      self.__onAcceptedCallback(fields)

  def getFields(self):
    return self.__fields
