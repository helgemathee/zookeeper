import sys
from PySide import QtCore, QtGui

class zkApp(object):

  __app = None

  def __init__(self):
    if not zkApp.__app:
      zkApp.__app = QtGui.QApplication(sys.argv)

  def exec_(self):
    zkApp.__app.exec_()  
