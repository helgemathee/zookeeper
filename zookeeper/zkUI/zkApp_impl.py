import sys
from PySide import QtCore, QtGui

class zkApp(object):

  __app = None

  def __init__(self):
    self.__app = QtGui.QApplication(sys.argv)

  def exec_(self):
    self.__app.exec_()  
