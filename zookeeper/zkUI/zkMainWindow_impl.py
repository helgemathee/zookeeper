import os
from PySide import QtCore, QtGui

class zkMainWindow(QtGui.QMainWindow):

  __centralWidget = None

  def __init__(self, title, parent = None):
    super(zkMainWindow, self).__init__(parent)

    self.setWindowTitle('ZooKeeper '+title)
    self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

    iconPath = os.path.join(os.path.split(__file__)[0], 'logo_low.png')
    icon = QtGui.QIcon(iconPath)
    self.setWindowIcon(icon)

    self.__centralWidget = QtGui.QWidget(self)
    self.setCentralWidget(self.__centralWidget)

    layout = QtGui.QVBoxLayout()
    self.__centralWidget.setLayout(layout)

    logoPath = os.path.join(os.path.split(__file__)[0], 'logo_dialog.png')
    logoPixmap = QtGui.QPixmap(logoPath)
    logoLable = QtGui.QLabel(self.__centralWidget)
    logoLable.setPixmap(logoPixmap)
    layout.addWidget(logoLable, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

  def addWidgetToCentral(self, widget, stretch = 0, align = 0):
    layout = self.__centralWidget.layout()
    widget.setParent(self.__centralWidget)
    layout.addWidget(widget, stretch, align)
