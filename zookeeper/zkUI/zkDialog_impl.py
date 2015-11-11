import os
from PySide import QtCore, QtGui

class zkDialog(QtGui.QDialog):

  __edits = None

  def __init__(self, parent = None):
    super(zkDialog, self).__init__(parent)

    # palette = self.palette()
    # palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    # palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25,25,25))
    # palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
    # palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    # palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    # palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    # palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    # palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    # palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    # self.setPalette(palette)

    self.setWindowTitle('ZooKeeper %s' % self.getDialogName())
    self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)

    iconPath = os.path.join(os.path.split(__file__)[0], 'logo_low.png')
    icon = QtGui.QIcon(iconPath)
    self.setWindowIcon(icon)

    layout = QtGui.QVBoxLayout()
    self.setLayout(layout)

    logoPath = os.path.join(os.path.split(__file__)[0], 'logo_dialog.png')
    logoPixmap = QtGui.QPixmap(logoPath)
    logoLable = QtGui.QLabel(self)
    logoLable.setPixmap(logoPixmap)
    layout.addWidget(logoLable)

    gridWidget = QtGui.QWidget(self)
    layout.addWidget(gridWidget)

    gridLayout = QtGui.QGridLayout()
    gridWidget.setLayout(gridLayout)

    self.__edits = {}

    fields = self.getFields()
    offset = 0
    for field in fields:
      tooltip = field.get('tooltip', '')
      label = QtGui.QLabel(field['name'], gridWidget)
      label.setToolTip(tooltip)
      gridLayout.addWidget(label, offset, 0)
      edit = None
      if field['type'] == 'bool':
        edit = QtGui.QCheckBox(gridWidget)
        if field['value']:
          edit.setCheckState(QtCore.Qt.Checked)
        else:
          edit.setCheckState(QtCore.Qt.Unchecked)
        gridLayout.addWidget(edit, offset, 1)
      elif field['type'] == 'int':
        edit = QtGui.QLineEdit(gridWidget)
        validator = QtGui.QIntValidator()
        edit.setValidator(validator)
        edit.setText(str(field['value']))
        gridLayout.addWidget(edit, offset, 1)
      elif field['type'] == 'str':
        edit = QtGui.QLineEdit(gridWidget)
        edit.setText(str(field['value']))
        gridLayout.addWidget(edit, offset, 1)
      elif field['type'] == 'folder':
        subWidget = QtGui.QWidget(gridWidget)
        subWidget.setContentsMargins(0, 0, 0, 0);
        subLayout = QtGui.QHBoxLayout()
        subWidget.setLayout(subLayout)
        subLayout.setContentsMargins(0, 0, 0, 0);

        edit = QtGui.QLineEdit(gridWidget)
        edit.setText(str(field['value']))
        subLayout.addWidget(edit)

        def setupButton(button, edit, name):
          def buttonClicked():
            result = QtGui.QFileDialog.getExistingDirectory(self, 'Pick '+name, edit.text())
            if len(result) > 0:
              edit.setText(result)
          button.clicked.connect(buttonClicked)

        button = QtGui.QPushButton('...', subWidget)
        button.setMaximumWidth(40)
        setupButton(button, edit, field['name'])

        subLayout.addWidget(button)
        gridLayout.addWidget(subWidget, offset, 1)
      elif field['type'] == 'combo':
        edit = QtGui.QComboBox(gridWidget)
        if not 'comboitems' in field:
          raise Exception('combo used without comboitems.')

        pairs = field['comboitems']
        for pair in pairs:
          edit.addItem(pair[1], pair[0])

        for i in range(len(pairs)):
          if pairs[i][0] == field['value']:
            edit.setCurrentIndex(i)
            break

        gridLayout.addWidget(edit, offset, 1)

      if not edit is None:
        edit.setToolTip(tooltip)
        if field.get('readonly', False):
          edit.setEnabled(False)
      self.__edits[field['name']] = edit

      offset = offset + 1

    buttonsWidget = QtGui.QDialogButtonBox(self)
    buttonsWidget.addButton(QtGui.QDialogButtonBox.Cancel)
    buttonsWidget.addButton(QtGui.QDialogButtonBox.Ok)
    layout.addWidget(buttonsWidget)

    def _onCanceled():
      self.onCanceled()
      self.close()

    def _onAccepted():
      fields = self.getFields()
      for field in fields:
        edit = self.__edits[field['name']]
        if field['type'] == 'bool':
          field['value'] = edit.checkState() == QtCore.Qt.Checked
        elif field['type'] == 'int':
          field['value'] = int(edit.text())
        elif field['type'] == 'str':
          field['value'] = edit.text()
        elif field['type'] == 'folder':
          field['value'] = edit.text()
        elif field['type'] == 'combo':
          field['value'] = edit.itemData(edit.currentIndex())
      self.onAccepted(fields)
      self.close()

    buttonsWidget.rejected.connect(_onCanceled)
    buttonsWidget.accepted.connect(_onAccepted)

  # virtual: to be implemented
  def getDialogName(self):
    return ''
  
  # virtual: to be implemented
  def getFields(self):
    return []

  # virtual: to be implemented
  def onCanceled(self):
    pass

  # virtual: to be implemented
  def onAccepted(self, fields):
    pass    
