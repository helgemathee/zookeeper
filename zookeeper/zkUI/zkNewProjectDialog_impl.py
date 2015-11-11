from zkCallbackDialog_impl import zkCallbackDialog

class zkNewProjectDialog(zkCallbackDialog):

  def __init__(self, onAcceptedCallback, onRejectedCallback, parent = None):
    super(zkNewProjectDialog, self).__init__(onAcceptedCallback, onRejectedCallback, parent)

  def getDialogName(self):
    return 'New Project'
  
  def getFields(self):
    return [
      {'name': 'name', 'value': 'Project', 'type': 'str'}
    ]

