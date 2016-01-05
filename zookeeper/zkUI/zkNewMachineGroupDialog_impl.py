from zkCallbackDialog_impl import zkCallbackDialog

class zkNewMachineGroupDialog(zkCallbackDialog):

  def __init__(self, onAcceptedCallback, onRejectedCallback, parent = None):
    super(zkNewMachineGroupDialog, self).__init__(onAcceptedCallback, onRejectedCallback, parent)

  def getDialogName(self):
    return 'New Machine Group'
  
  def getFields(self):
    return [
      {'name': 'name', 'value': 'Group', 'type': 'str'}
    ]

