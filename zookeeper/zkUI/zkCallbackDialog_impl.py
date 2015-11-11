import copy
from zkDialog_impl import zkDialog

class zkCallbackDialog(zkDialog):

  __onRejectedCallback = None
  __onAcceptedCallback = None

  def __init__(self, onAcceptedCallback, onRejectedCallback, parent = None):
    self.__onAcceptedCallback = onAcceptedCallback
    self.__onRejectedCallback = onRejectedCallback
    super(zkCallbackDialog, self).__init__(parent)

  def onCanceled(self):
    if self.__onRejectedCallback:
      self.__onRejectedCallback()

  def onAccepted(self, fields):
    if self.__onAcceptedCallback:
      self.__onAcceptedCallback(fields)
